import { marked } from "marked";

const tokenizer = {
  link(src: string) {
    const match = src.match(/^\[\[(\w+)\]\]/);
    if (match) {
      return {
        type: "link",
        raw: match[0],
        href: match[1],
        text: "",
        tokens: [],
      };
    }
    return false;
  },
} as any;

const renderer = {
  link({ raw, href }: { raw: string; href: string }) {
    if (raw.match(/^\[\[\w+\]\]$/)) {
      return `<ResourceLink uid="${href}" />`;
    }
    return false;
  },
  paragraph({ raw }: { raw: string }) {
    const match = raw.match(/^!\[\[(\w+(,[\w]+)*)\]\]$/);
    if (match) {
      return `<ResourceGrid uids="${match[1]}" />`;
    }
    return false;
  },
} as any;

marked.use({ tokenizer, renderer });

export function parse(markdown: string): string {
  return marked.parse(markdown) as string;
}
