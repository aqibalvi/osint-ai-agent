import React, { useState } from "react";

interface WelcomeScreenProps {
  handleSubmit: (
    query: string,
    retrievalModel: string,
    synthesisModel: string
  ) => void;
  onCancel: () => void;
  isLoading: boolean;
}

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({
  handleSubmit,
  onCancel,
  isLoading,
}) => {
  const [input, setInput] = useState("");
  const [retrievalModel, setRetrievalModel] = useState("gpt-4o-mini-search-preview");
  const [synthesisModel, setSynthesisModel] = useState("gemini-1.5-pro");

  const handleLocalSubmit = () => {
    if (input.trim()) {
      handleSubmit(input.trim(), retrievalModel, synthesisModel);
    }
  };

  return (
    <div className="text-center space-y-6 mt-20">
      <h1 className="text-4xl font-bold">
        OSINT <span className="text-purple-500">Intelligence Agent</span>
      </h1>
      <p className="text-lg text-gray-400 max-w-2xl mx-auto">
        Discover public intelligence by investigating entities across social
        media, publications, patents, and more. Powered by LangGraph, Claude,
        Gemini, and GPT-4o.
      </p>

      <input
        className="w-full max-w-xl px-4 py-3 rounded-lg bg-neutral-800 border border-neutral-700 text-white placeholder-gray-500"
        placeholder="e.g., Investigate Ali Khaledi Nasab's AI research contributions"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleLocalSubmit()}
        disabled={isLoading}
      />

      <div className="flex justify-center space-x-4">
        <select
          className="bg-neutral-800 text-white border border-neutral-700 p-2 rounded-md"
          value={retrievalModel}
          onChange={(e) => setRetrievalModel(e.target.value)}
        >
          <option value="gpt-4o-search-preview">GPT-4o</option>
          <option value="gpt-4o-mini-search-preview">GPT-4o Mini</option>
          {/* <option value="claude-opus-4-20250514">Claude 4 Opus</option> */}
        </select>

        <select
          className="bg-neutral-800 text-white border border-neutral-700 p-2 rounded-md"
          value={synthesisModel}
          onChange={(e) => setSynthesisModel(e.target.value)}
        >
          <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
          <option value="gemini-2.0-flash">Gemini 2.0 Flash</option>
        </select>
      </div>

      <div className="flex justify-center space-x-4">
        <button
          onClick={handleLocalSubmit}
          className="px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg text-white font-semibold disabled:opacity-50"
          disabled={isLoading}
        >
          Generate OSINT Report
        </button>
      </div>
    </div>
  );
};

export default WelcomeScreen;
