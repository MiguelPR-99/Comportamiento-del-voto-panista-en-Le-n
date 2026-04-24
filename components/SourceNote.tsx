type SourceNoteProps = {
  sourceLines: string[];
  authorNote: string;
};

export function SourceNote({ sourceLines, authorNote }: SourceNoteProps) {
  return (
    <section className="source-note">
      <h2 className="panel-title">Fuente y nota</h2>
      {sourceLines.map((line) => (
        <p key={line} className="source-line">
          {line}
        </p>
      ))}
      <p className="author-line">{authorNote}</p>
    </section>
  );
}
