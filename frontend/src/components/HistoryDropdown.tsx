// frontend/src/components/HistoryDropdown.tsx
import React, { useEffect, useState } from 'react';

interface HistoryDropdownProps {
  onSelect: (filename: string) => void;
}

const HistoryDropdown: React.FC<HistoryDropdownProps> = ({ onSelect }) => {
  const [files, setFiles] = useState<string[]>([]);

  useEffect(() => {
    fetch('http://localhost:8000/osint/history')
      .then(res => res.json())
      .then(setFiles)
      .catch(console.error);
  }, []);

  return (
    <div className="p-2">
      <label className="font-semibold">Load Past Investigation:</label>
      <select
        className="ml-2 p-1 border border-gray-300 rounded"
        onChange={e => onSelect(e.target.value)}
        defaultValue=""
      >
        <option value="" disabled>Select investigation...</option>
        {files.map((f, i) => (
          <option key={i} value={f}>{f}</option>
        ))}
      </select>
    </div>
  );
};

export default HistoryDropdown;
