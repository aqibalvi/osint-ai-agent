// frontend/src/components/ReportViewer.tsx
import React from "react";
import ReactMarkdown from "react-markdown";

interface Citation {
  url: string;
  title?: string;
}

interface Props {
  report: string;
  citations?: Citation[]; // made optional
  flaggedIssues?: string[]; // made optional
  credibilityScore?: number; // made optional
  onNewSearch: () => void;
}

const ReportViewer: React.FC<Props> = ({
  report,
  citations = [], // default: empty array
  flaggedIssues = [],
  credibilityScore = 0,
  onNewSearch,
}) => {
  return (
    <div className="px-6 py-4 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-2">🧾 OSINT Intelligence Report</h2>
      <ReactMarkdown className="prose prose-invert">{report}</ReactMarkdown>

      {citations.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold">🔗 Citations</h3>
          <ul className="list-disc ml-6">
            {citations.map((c, i) => (
              <li key={i}>
                <a href={c.url} target="_blank" rel="noopener noreferrer">
                  {c.title || c.url}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}

      {flaggedIssues.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold">🚨 Flagged Issues</h3>
          <ul className="list-disc ml-6 text-red-500">
            {flaggedIssues.map((issue, i) => (
              <li key={i}>{issue}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-4">
        <h3 className="text-lg font-semibold">🧠 Credibility Score</h3>
        <p className="text-yellow-300 font-bold">{credibilityScore}/10</p>
      </div>

      <div className="mt-6">
        <button
          className="bg-blue-600 hover:bg-blue-500 text-white font-bold py-2 px-4 rounded"
          onClick={onNewSearch}
        >
          🔄 Start New Investigation
        </button>
      </div>
    </div>
  );
};

export default ReportViewer;
