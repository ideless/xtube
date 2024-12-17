interface BaseRecord {
  uid: string;
  original_name: string;
  original_size: number;
  original_hash: string;
  title: string;
  description: string;
  encrypted: boolean;
  iv?: string;
  creation_time: string;
  kind: string;
  mime_type: string;
  thumbnail: string;
  file: string;
  hash: string;
  size: number;
}

interface VideoRecord extends BaseRecord {
  kind: "video";
  duration: number;
}

interface ImageRecord extends BaseRecord {
  kind: "image";
}

interface BookRecord extends BaseRecord {
  kind: "book";
  author: string;
  language: string;
}

interface NoteRecord extends BaseRecord {
  kind: "note";
}

interface FileRecord extends BaseRecord {
  kind: "file";
}

type AnyRecord =
  | VideoRecord
  | ImageRecord
  | BookRecord
  | NoteRecord
  | FileRecord;
