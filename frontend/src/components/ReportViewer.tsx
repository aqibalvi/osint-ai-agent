// frontend/src/components/ReportViewer.tsx
import React from "react";
import ReactMarkdown from "react-markdown";

interface Citation {
  url: string;
  title?: string;
}

interface RiskAssessment {
  risk_score: number | string;
  verdict: string;
  risk_signals: string[];
}

interface Props {
  report: string;
  citations?: Citation[];
  flaggedIssues?: string[];
  credibilityScore?: number;
  riskAssessment?: RiskAssessment;
  onNewSearch: () => void;
}

const ReportViewer: React.FC<Props> = ({
  report,
  citations = [],
  flaggedIssues = [],
  credibilityScore = 0,
  riskAssessment,
  onNewSearch,
}) => {
  return (
    <div className="bg-neutral-900 text-white px-6 py-6 max-w-4xl mx-auto rounded-lg shadow-lg border border-neutral-700">
      <h2 className="text-3xl font-bold mb-6 border-b border-neutral-700 pb-2">
        🧾 OSINT Intelligence Report
      </h2>

      <section className="mb-8">
        <ReactMarkdown className="prose prose-invert">{report}</ReactMarkdown>
      </section>

      {citations.length > 0 && (
        <section className="mb-8">
          <h3 className="text-xl font-semibold text-blue-400 mb-2">🔗 Citations</h3>
          <ul className="list-disc ml-6 space-y-1">
            {citations.map((c, i) => (
              <li key={i}>
                <a
                  href={c.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-300 hover:underline"
                >
                  {c.title || c.url}
                </a>
              </li>
            ))}
          </ul>
        </section>
      )}

      {flaggedIssues.length > 0 && (
        <section className="mb-8">
          <h3 className="text-xl font-semibold text-red-400 mb-2">🚨 Flagged Issues</h3>
          <ul className="list-disc ml-6 text-red-300 space-y-1">
            {flaggedIssues.map((issue, i) => (
              <li key={i}>{issue}</li>
            ))}
          </ul>
        </section>
      )}

      <section className="mb-8">
        <h3 className="text-xl font-semibold text-yellow-400 mb-1">🧠 Credibility Score</h3>
        <p className="text-yellow-300 text-lg font-bold">{credibilityScore}/10</p>
      </section>

      {riskAssessment && (
        <section className="mb-8">
          <h3 className="text-xl font-semibold text-red-300 mb-2">🔒 Risk Assessment</h3>
          <p className="text-lg font-bold text-red-400">
            Risk Level: {riskAssessment.verdict} ({riskAssessment.risk_score}/10)
          </p>
          <ul className="list-disc ml-6 mt-2 text-red-200 space-y-1">
            {riskAssessment.risk_signals.map((signal, i) => (
              <li key={i}>{signal}</li>
            ))}
          </ul>
        </section>
      )}

      <div className="mt-6 text-center">
        <button
          className="bg-blue-600 hover:bg-blue-500 text-white font-semibold py-2 px-6 rounded-lg shadow-md transition duration-200"
          onClick={onNewSearch}
        >
          🔄 Start New Investigation
        </button>
      </div>
    </div>
  );
};

export default ReportViewer;
