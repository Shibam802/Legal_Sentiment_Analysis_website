import React, { useState } from "react";

function App() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);

  const analyzeSentiment = async () => {
    try {
      const response = await fetch("http://localhost:8000/analyze_text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Error:", error);
      setResult({ summary: "⚠️ Error analyzing sentiment" });
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 p-6">
      <div className="bg-white/90 backdrop-blur-lg shadow-2xl rounded-2xl p-8 w-[500px] border border-gray-200">
        
        {/* Title */}
        <h1 className="text-3xl font-bold text-center text-indigo-800 mb-6 flex items-center justify-center gap-2">
          ⚖️ Legal Sentiment Analyzer 🚀
        </h1>

        {/* Textarea */}
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste your legal text here..."
          className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:outline-none resize-none h-32 bg-gray-50"
        />

        {/* Button */}
        <button
          onClick={analyzeSentiment}
          className="mt-4 w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold py-2 rounded-lg shadow-md hover:from-indigo-700 hover:to-purple-700 transition"
        >
          Analyze Sentiment
        </button>

        {/* Result Section */}
        {result && (
          <div className="mt-6 p-5 bg-gradient-to-r from-gray-100 to-gray-200 rounded-xl shadow-inner">
            <h2 className="text-lg font-semibold text-gray-800 mb-2">📊 Result:</h2>
            
            {/* Summary */}
            <p className="mt-2 text-purple-700 font-medium whitespace-pre-line">
              {result.summary}
            </p>

            {/* Detailed Results */}
            {result.results && (
              <div className="mt-4 max-h-40 overflow-y-auto">
                <table className="w-full text-sm border-collapse">
                  <thead>
                    <tr className="bg-gray-300 text-gray-800">
                      <th className="p-2 border">Sentence</th>
                      <th className="p-2 border">Sentiment</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.results.map((r, idx) => (
                      <tr key={idx} className="even:bg-gray-100">
                        <td className="p-2 border">{r.text}</td>
                        <td
                          className={`p-2 border font-semibold ${
                            r.sentiment === "Positive"
                              ? "text-green-600"
                              : r.sentiment === "Negative"
                              ? "text-red-600"
                              : "text-gray-700"
                          }`}
                        >
                          {r.sentiment}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;





