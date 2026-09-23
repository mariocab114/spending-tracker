import { useState } from "react";
import type { ChangeEvent } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:5000/api/categorize";

// TypeScript types that describe the JSON the Flask API sends back
interface Transaction {
  date?: string;
  description: string;
  amount: number;
  category: string;
}

interface CategoryTotal {
  category: string;
  total: number;
}

interface CategorizeResponse {
  transactions: Transaction[];
  category_totals: CategoryTotal[];
  total_spent: number;
}

const formatMoney = (value: number) =>
  value.toLocaleString("en-US", { style: "currency", currency: "USD" });

function App() {
  const [data, setData] = useState<CategorizeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError(null);
    setData(null);

    // Package the file the same way curl did with -F "file=@..."
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(API_URL, { method: "POST", body: formData });
      const result = await response.json();

      if (!response.ok) {
        setError(result.error ?? "Something went wrong.");
        return;
      }
      setData(result as CategorizeResponse);
    } catch {
      setError("Could not reach the API. Is api.py running?");
    } finally {
      setLoading(false);
    }
  }

  const maxTotal = data
    ? Math.max(...data.category_totals.map((c) => c.total), 1)
    : 1;

  return (
    <div className="app">
      <h1>💰 Spending Tracker</h1>
      <p className="subtitle">
        Upload a CSV of your transactions to see them categorized and summarized.
      </p>

      <label className="upload">
        Choose CSV file
        <input type="file" accept=".csv" onChange={handleFileChange} />
      </label>

      {loading && <p className="status">Categorizing...</p>}
      {error && <p className="status error">{error}</p>}

      {data && (
        <>
          <section className="card">
            <h2>Total Spent</h2>
            <p className="total">{formatMoney(data.total_spent)}</p>
          </section>

          <section className="card">
            <h2>Spending by Category</h2>
            {data.category_totals.map((c) => (
              <div className="bar-row" key={c.category}>
                <span>{c.category}</span>
                <div className="bar-track">
                  <div
                    className="bar-fill"
                    style={{ width: `${(c.total / maxTotal) * 100}%` }}
                  />
                </div>
                <span className="bar-amount">{formatMoney(c.total)}</span>
              </div>
            ))}
          </section>

          <section className="card">
            <h2>All Transactions</h2>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Description</th>
                    <th>Category</th>
                    <th className="amount">Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {data.transactions.map((t, i) => (
                    <tr key={`${t.date}-${i}`}>
                      <td>{t.date}</td>
                      <td>{t.description}</td>
                      <td>
                        <span className="tag">{t.category}</span>
                      </td>
                      <td className="amount">{formatMoney(t.amount)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </div>
  );
}

export default App;