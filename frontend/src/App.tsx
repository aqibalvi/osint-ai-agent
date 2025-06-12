import { useState } from "react";
import ReportViewer from "@/components/ReportViewer";
import WelcomeScreen from "@/components/WelcomeScreen";
import StepLoader from "@/components/StepLoader";
import { useNavigate } from "react-router-dom";

interface ReportData {
  report: string;
  credibility_score: number;
  flagged_issues: string[];
  parsed: Record<string, string>;
  citations: { title: string; url: string }[];
}

function App() {
  const [inputValue, setInputValue] = useState("");
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [statusLog, setStatusLog] = useState<string[]>([]);
  const navigate = useNavigate();

  const handleSubmit = async (
    query: string,
    retrievalModel: string,
    synthesisModel: string
  ) => {
    setInputValue(query);
    setIsLoading(true);
    setReportData(null);
    setStatusLog([]);

    try {
      const response = await fetch("http://localhost:8000/osint/investigate-stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query,
          retrieval_model: retrievalModel,
          synthesis_model: synthesisModel,
        }),
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (reader) {
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          const lines = buffer.split("\n");
          buffer = lines.pop()!; // keep incomplete line

          for (const line of lines) {
            if (!line.trim()) continue;

            const data = JSON.parse(line.trim());

            if (data.step) {
              setStatusLog((prev) => [...prev, `🛠 ${data.step}`]);
            } else if (data.search) {
              setStatusLog((prev) => [...prev, `${data.search}`]);
            } else if (data.final) {
              setReportData(data.final);
              setIsLoading(false);
            }
          }
        }
      }
    } catch (err) {
      alert("Error: Unable to retrieve OSINT report.");
      console.error(err);
      setIsLoading(false);
    }
  };

  const handleNewSearch = () => {
    setReportData(null);
    setInputValue("");
    setStatusLog([]);
  };

  return (
    <div className="min-h-screen bg-neutral-900 text-white font-sans flex flex-col items-center justify-start py-6 px-4">
      <div className="w-full max-w-4xl">
        {!reportData && !isLoading && (
          <WelcomeScreen
            handleSubmit={handleSubmit}
            onCancel={handleNewSearch}
            isLoading={isLoading}
          />
        )}

        {!reportData && isLoading && (
          <StepLoader log={statusLog} />
        )}

        {reportData && (
          <ReportViewer
            report={reportData.report}
            credibilityScore={reportData.credibility_score}
            flaggedIssues={reportData.flagged_issues}
            citations={reportData.citations || []}
            onNewSearch={handleNewSearch}
          />
        )}
      </div>
    </div>
  );
}

export default App;
