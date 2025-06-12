// frontend/src/components/StepLoader.tsx
import React from "react";

interface Props {
  log: string[];
}

const StepLoader: React.FC<Props> = ({ log }) => {
  return (
    <div className="text-left mt-12 px-6">
      <h2 className="text-xl font-semibold mb-4 text-blue-400">
        🔄 Generating OSINT Report
      </h2>
      <div className="bg-neutral-800 border border-neutral-700 rounded-lg p-4 space-y-2 max-h-[400px] overflow-y-auto">
        {log.length === 0 && (
          <p className="text-gray-400 italic">Initializing pipeline...</p>
        )}
        {log.map((entry, index) => (
          <p key={index} className="text-sm text-gray-200">
            {entry}
          </p>
        ))}
      </div>
    </div>
  );
};

export default StepLoader;