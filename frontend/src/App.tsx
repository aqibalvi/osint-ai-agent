import { useState, useEffect } from "react";
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
  const [savedInvestigations, setSavedInvestigations] = useState<string[]>([]);
  const [selectedInvestigation, setSelectedInvestigation] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchSavedInvestigations = async () => {
      try {
        const res = await fetch("http://localhost:8000/osint/history");
        const data = await res.json();
        setSavedInvestigations(data);
      } catch (err) {
        console.error("Failed to fetch saved investigations", err);
      }
    };

    fetchSavedInvestigations();
  }, []);

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
          buffer = lines.pop()!;

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
    setSelectedInvestigation(null);
  };

  const loadSavedInvestigation = async (filename: string) => {
    setIsLoading(true);
    setStatusLog([]);
    try {
      const res = await fetch(`http://localhost:8000/osint/history/load/${filename}`);
      const data = await res.json();

      const formatted: ReportData = {
        report: data.report,
        credibility_score: data.judgement?.credibility_score ?? 0,
        flagged_issues: data.judgement?.flagged_issues ?? [],
        parsed: data.parsed,
        citations: Object.values(data.retrievals || {}).flatMap((task: any) =>
          (task.citations || []).map((c: any) => ({
            title: c.title,
            url: c.url,
          }))
        ),
      };

      setReportData(formatted);
      setInputValue(data.query);
      setIsLoading(false);
    } catch (err) {
      alert("Error loading saved investigation.");
      console.error(err);
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-900 text-white font-sans flex flex-col items-center justify-start py-6 px-4">
      <div className="w-full max-w-4xl">
        <div className="mb-6">
          <label htmlFor="history-select" className="block text-lg font-semibold mb-2 text-white">
            📁 Load Saved Investigation:
          </label>
          <div className="relative inline-block w-full max-w-md">
            <select
              id="history-select"
              className="block w-full appearance-none bg-neutral-800 text-white border border-neutral-700 px-4 py-2 pr-10 rounded-lg shadow focus:outline-none focus:ring-2 focus:ring-blue-500"
              onChange={(e) => {
                const file = e.target.value;
                if (file) {
                  setSelectedInvestigation(file);
                  loadSavedInvestigation(file);
                }
              }}
              value={selectedInvestigation || ""}
            >
              <option value="" className="text-black">-- Select a saved report --</option>
              {savedInvestigations.map((file) => (
                <option key={file} value={file} className="text-black">
                  {file.replace(".json", "")}
                </option>
              ))}
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-white">
              <svg className="w-5 h-5" viewBox="0 0 20 20" fill="currentColor">
                <path
                  fillRule="evenodd"
                  d="M10 14a1 1 0 01-.707-.293l-4-4a1 1 0 111.414-1.414L10 11.586l3.293-3.293a1 1 0 111.414 1.414l-4 4A1 1 0 0110 14z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
          </div>
        </div>

        {!reportData && !isLoading && (
          <WelcomeScreen
            handleSubmit={handleSubmit}
            onCancel={handleNewSearch}
            isLoading={isLoading}
          />
        )}

        {!reportData && isLoading && <StepLoader log={statusLog} />}

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
