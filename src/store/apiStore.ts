import { defineStore } from "pinia";
import { ref } from "vue";
import YAML from "yaml";
import { hexToBytes, getBytesHash } from "./utils";
import axios from "axios";

export const useApiStore = defineStore("api", () => {
  // mutable data
  const dbEncAlgo = "AES-CBC";
  let dbKeyHex: string | null = null;
  let dbKey: CryptoKey | null = null;
  let dbIv: Uint8Array | null = null;

  // reactive data
  const records = ref<AnyRecord[]>([]);
  const recordByUid = ref<Record<string, AnyRecord>>({});
  const loggedIn = ref(false);

  // functions
  async function verifyKey(key: string) {
    let response = await fetch("/data/key_info.yaml", { cache: "no-cache" });

    if (!response.ok) {
      await axios.post("/api/init", key);
      response = await fetch("/data/key_info.yaml", { cache: "no-cache" });
      if (!response.ok) return false;
    }

    const yamlText = await response.text();
    const keyInfo = YAML.parse(yamlText) as { key_hash: string; iv: string };

    const key_bytes = hexToBytes(key);
    const keyHashFull = await getBytesHash(key_bytes, "SHA-256");
    const keyHash = keyHashFull.toLowerCase().substring(0, 6);

    if (keyHash === keyInfo.key_hash) {
      document.cookie = `key=${key}`;

      dbKeyHex = key;
      dbKey = await crypto.subtle.importKey(
        "raw",
        key_bytes,
        dbEncAlgo,
        false,
        ["decrypt"],
      );
      dbIv = hexToBytes(keyInfo.iv);

      return true;
    } else {
      return false;
    }
  }

  async function fetchRecords() {
    if (dbKey === null || dbIv === null) {
      throw new Error("Key or IV for database is not set");
    }

    const response = await fetch("/data/db.yaml.enc", { cache: "no-cache" });
    const responseBuffer = await response.arrayBuffer();
    const yamlBuffer = await window.crypto.subtle.decrypt(
      {
        name: dbEncAlgo,
        iv: dbIv,
      },
      dbKey,
      responseBuffer,
    );
    const yamlText = new TextDecoder().decode(yamlBuffer);
    records.value = (YAML.parse(yamlText) || []) as AnyRecord[];
    // recreate recordByUid
    const newRecordByUid: Record<string, AnyRecord> = {};
    records.value.forEach((r) => {
      newRecordByUid[r.uid] = r;
    });
    recordByUid.value = newRecordByUid;
  }

  function getRecord(uid: string, check: true): AnyRecord;
  function getRecord(uid: string, check?: false): AnyRecord | undefined;
  function getRecord(uid: string, check?: boolean): AnyRecord | undefined {
    const record = recordByUid.value[uid];

    if (check && !record) {
      throw new Error("Record not found");
    }

    return record;
  }

  async function fetchAndDecrypt(path: string, decrypt = false, iv?: string) {
    const response = await fetch(`/data/${path}`, { cache: "no-cache" });
    const responseBuffer = await response.arrayBuffer();

    if (decrypt) {
      if (!dbKey || !iv) {
        throw new Error("Key or IV is missing for encrypted file");
      }

      const decryptedBuffer = await crypto.subtle.decrypt(
        {
          name: dbEncAlgo,
          iv: hexToBytes(iv),
        },
        dbKey,
        responseBuffer,
      );

      return decryptedBuffer;
    } else {
      return responseBuffer;
    }
  }

  async function fetchThumbnail(record: AnyRecord) {
    return fetchAndDecrypt(record.thumbnail, record.encrypted, record.iv);
  }

  async function fetchFile(record: AnyRecord) {
    return fetchAndDecrypt(record.file, record.encrypted, record.iv);
  }

  async function uploadMedia(data: {
    file: File;
    kind: string;
    title: string;
    description?: string;
    thumbnail?: File;
    hls_time?: number;
    bitrate?: string;
    encoding?: string;
    author?: string;
    language?: string;
    toc_title?: string;
    max_ctl?: number;
  }) {
    if (!dbKeyHex) {
      throw new Error("Key is not set");
    }

    const formData = new FormData();

    formData.append("key", dbKeyHex);
    Object.entries(data).forEach(([key, value]) => {
      if (value === undefined) return;
      if (value instanceof File) {
        formData.append(key, value);
      } else {
        formData.append(key, String(value));
      }
    });

    await axios.put("/api/media", formData);
  }

  async function updateMedia(
    uid: string,
    title?: string,
    description?: string,
    thumbnail?: File,
  ) {
    if (!dbKeyHex) {
      throw new Error("Key is not set");
    }

    const formData = new FormData();

    formData.append("uid", uid);
    formData.append("key", dbKeyHex);
    if (title) formData.append("title", title);
    if (description) formData.append("description", description);
    if (thumbnail) formData.append("thumbnail", thumbnail);

    await axios.patch("/api/media", formData);
  }

  async function deleteMedia(uids: string[]) {
    if (!dbKeyHex) {
      throw new Error("Key is not set");
    }

    await axios.delete("/api/media", {
      data: {
        key: dbKeyHex,
        uids,
      },
    });
  }

  async function createNote(
    title: string,
    content: string,
    description?: string,
    thumbnail?: File,
  ) {
    if (!dbKeyHex) {
      throw new Error("Key is not set");
    }

    const formData = new FormData();

    formData.append("key", dbKeyHex);
    formData.append("title", title);
    formData.append("content", content);
    if (description) formData.append("description", description);
    if (thumbnail) formData.append("thumbnail", thumbnail);

    await axios.put("/api/note", formData);
  }

  async function updateNote(uid: string, content: string) {
    if (!dbKeyHex) {
      throw new Error("Key is not set");
    }

    await axios.patch("/api/note", {
      key: dbKeyHex,
      uid,
      content,
    });
  }

  // expose
  return {
    // variables
    records,
    recordByUid,
    loggedIn,
    // functions
    verifyKey,
    fetchRecords,
    getRecord,
    fetchAndDecrypt,
    fetchThumbnail,
    fetchFile,
    uploadMedia,
    updateMedia,
    deleteMedia,
    createNote,
    updateNote,
  };
});
