import { useState } from "react";
import axios from "axios";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyze = async () => {
    if (!file) {
      alert("Please upload a file");
      return;
    }

    const form = new FormData();
    form.append("file", file);

    setLoading(true);

    try {
      const res = await axios.post(
        "http://127.0.0.1:8000/analyze",
        form
      );

      setResult(res.data);
    } catch (err) {
      alert("Error connecting to backend");
    }

    setLoading(false);
  };

  return (
    <div style={{ padding: "40px", fontFamily: "Arial" }}>
      <h1>AI Financial Research Tool</h1>

      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <button onClick={analyze} style={{ marginLeft: "10px" }}>
        Analyze
      </button>

      {loading && <p>Analyzing transcript...</p>}

      {result && (
        <div style={{ marginTop: "20px" }}>
          <h2>Analysis Result</h2>

          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default App;