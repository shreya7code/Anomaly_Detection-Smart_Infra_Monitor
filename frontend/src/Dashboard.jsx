import { useEffect, useState } from "react";
import { Line } from 'react-chartjs-2';

// Setting up Chart.js for React
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  LineController,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

// Register all necessary chart types and features
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  LineController,
  Title,
  Tooltip,
  Legend,
  Filler
);


/*
Defines React component - Dashboard in the UI
*/
export default function Dashboard() {
    // metrics - stores latest metrics
    // anomalies - stores anomaly events detected    
    const [metrics, setMetrics] = useState([]);
    const [anomalies, setAnomalies] = useState([]);

    // runs once when the page is loaded with all the dependecies
    // starts a timer for fetchMetrics to call for every 5s
    useEffect(() => {
        // to fetch anomalies back, if it is lost after refresh
        fetchAnomalies();

        const interval = setInterval(() => {
        fetchMetrics();
        }, 5000);
        
        // stops if you leave the page
        return () => clearInterval(interval);
    }, []);

    async function fetchMetrics() {
        // calls FastAPI /metrics
        // converts the JSON to JS object
        const res = await fetch("http://localhost:8000/metrics");
        const data = await res.json();

        // if data exist then proceed to avoid any erors if backend returns an empty array
        if (data.cpu && data.cpu.length > 0) {

            // this takes the most recent values of the cpu metrics and converts into payload
            const latestIndex = data.cpu.length - 1;
            
            const payload = {
                cpu: data.cpu[latestIndex],
                memory: data.memory[latestIndex],
                disk: data.disk[latestIndex],
            };
            
            // the payload is then send to the POST method - /predict ML model
            const anomalyRes = await fetch("http://localhost:8000/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            // contains the predicted result from the ML model
            const result = await anomalyRes.json();

            // Anomaly displayed if the predicted result is anomaly and logs in the console
            // Here, anomalies - the array of all the anomalies detected so far
            // setAnomalies is a updater function and adds the latest anomaly to the prev aomalies (..prev)
            // And then create a new object  with new timestamp field
            if (result.prediction === "anomaly") {
                console.log("🚨 Anomaly Detected!", payload);

                // setAnomalies(prev => [...prev, { ...payload, timestamp: data.timestamps[latestIndex] }]);
                // Saves the anomalies to the InfluxDB
                await fetch("http://localhost:8000/anomaly", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        ...payload,
                        timestamp: data.timestamps[latestIndex]
                    })
                })

                setAnomalies(prev => [
                            ...prev,
                            {
                                ...payload,
                                timestamp: data.timestamps[latestIndex]
                            }
                        ]);

            }

            setMetrics(data);
        }
  }

  async function fetchAnomalies(){
    const res = await fetch("http://localhost:8000/anomalies");
    const data = await res.json();

    if (data && data.length > 0) {
        // normalize the timestamp field
        const anomaliesNormalized = data.map(item => ({
            ...item,
            timestamp: item._time
        }));

        setAnomalies(anomaliesNormalized);
    }
  }

  //takes the backend data and prepares a chart out of it
  let chartData = {
        labels: metrics.timestamps || [],
        datasets: [
            {
                label: 'CPU Usage (%)',
                data: metrics.cpu || [],
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                fill: true,
            },
            {
                label: 'Memory Usage (%)',
                data: metrics.memory || [],
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                fill: true,
            },
            {
                label: 'Disk Usage (%)',
                data: metrics.disk || [],
                borderColor: 'rgb(54, 162, 235)',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                fill: true,
            }
        ],
    };

  // this prints all metrics and anomalies as a pretty JSON
  return (
    <div className="min-vh-100 bg-light">
      <nav className="navbar navbar-dark bg-primary mb-4">
        <div className="container">
          <span className="navbar-brand mb-0 h1">Smart Infra Monitor</span>
        </div>
      </nav>

      <main className="container">
        <h1 className="display-4 text-primary text-center mb-5">
          Smart Infra Dashboard
        </h1>

        <div className="card shadow mb-5">
          <div className="card-header bg-primary text-white">
            Live Metrics
          </div>
          <div className="card-body">
            <Line
              data={chartData}
              options={{
                responsive: true,
                plugins: {
                  legend: { position: 'bottom' },
                  title: {
                    display: true,
                    text: 'Smart Infra Live Metrics',
                    font: { size: 18 }
                  },
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    title: {
                      display: true,
                      text: 'Usage (%)',
                    },
                  },
                  x: {
                    title: {
                      display: true,
                      text: 'Timestamp',
                    },
                  },
                },
              }}
            />
          </div>
        </div>

        <div className="card shadow">
          <div className="card-header bg-success text-white">
            Detected Anomalies
          </div>
          <div className="card-body">
            {anomalies.length > 0 ? (
              <div className="table-responsive">
                <table className="table table-bordered table-hover">
                  <thead className="thead-light">
                    <tr>
                      <th>Timestamp</th>
                      <th>CPU (%)</th>
                      <th>Memory (%)</th>
                      <th>Disk (%)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {anomalies.map((anomaly, index) => (
                      <tr
                        key={index}
                        className={
                          (anomaly.cpu > 85 || anomaly.memory > 85 || anomaly.disk > 90)
                            ? "table-danger"
                            : ""
                        }
                      >
                        <td>{new Date(anomaly.timestamp).toLocaleString()}</td>
                        <td>{anomaly.cpu.toFixed(2)}</td>
                        <td>{anomaly.memory.toFixed(2)}</td>
                        <td>{anomaly.disk.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-muted">No anomalies detected yet.</p>
            )}
          </div>
        </div>
      </main>
    </div>
  );

}
