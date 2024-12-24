export function hexToBytes(hex: string): Uint8Array {
  // Ensure the input string is valid
  if (hex.length % 2 !== 0) {
    throw new Error("Hex string must have an even number of characters");
  }

  const bytes = new Uint8Array(hex.length / 2);

  for (let i = 0; i < bytes.length; i++) {
    const hexByte = hex.substring(i * 2, i * 2 + 2);
    bytes[i] = Number.parseInt(hexByte, 16);
  }

  return bytes;
}

export async function getBytesHash(
  bytes: Uint8Array,
  algorithm: AlgorithmIdentifier,
) {
  const hashBuffer = await crypto.subtle.digest(algorithm, bytes);
  const hashArray = new Uint8Array(hashBuffer);
  const hashHex = Array.from(hashArray)
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
  return hashHex;
}

export function trimRecord<T extends Record<string, unknown>>(obj: T): T {
  const newObj = {} as T;

  for (const key in obj) {
    const value = obj[key];

    if (value !== undefined && value !== null) {
      newObj[key] = value;
    }
  }

  return newObj;
}

export function bytesToString(bytes: number) {
  if (bytes === 0) {
    return "0 B";
  }

  let e = Math.floor(Math.log(bytes) / Math.log(1024));
  return (
    (bytes / Math.pow(1024, e)).toFixed(2) + " " + " KMGTP".charAt(e) + "B"
  );
}
