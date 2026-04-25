import { normalizeEditorialText } from "@/lib/presentation";

type SourceNoteProps = {
  sourceLines: string[];
  authorNote: string;
};

export function SourceNote({ sourceLines, authorNote }: SourceNoteProps) {
  return (
    <section className="source-note">
      <h2 className="panel-title">{"Fuentes y cr\u00e9ditos"}</h2>
      {sourceLines.map((line) => (
        <p key={line} className="source-line">
          {normalizeEditorialText(line)}
        </p>
      ))}
      <p className="author-line">{normalizeEditorialText(authorNote)}</p>
    </section>
  );
}
