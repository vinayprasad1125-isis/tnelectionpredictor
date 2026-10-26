import React, { useState, useEffect } from 'react';
import { predictionService } from '../../services/predictionService';
import { analyticsService } from '../../services/analyticsService';
import { dataService } from '../../services/dataService';
import { Loading, ErrorMessage } from '../../components/common/Common';
import { BrainCircuit, Target, Activity, Clock, History } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const Predictions = () => {
  const [models, setModels] = useState({});
  const [constituencies, setConstituencies] = useState([]);
  const [selectedConst, setSelectedConst] = useState('');
  const [selectedYear, setSelectedYear] = useState(2031);
  
  const [prediction, setPrediction] = useState(null);
  const [historicalContext, setHistoricalContext] = useState(null);
  
  const [modelMetrics, setModelMetrics] = useState(null);
  const [predictionHistory, setPredictionHistory] = useState([]);
  const [historyPage, setHistoryPage] = useState(1);
  const [historyTotal, setHistoryTotal] = useState(0);
  
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchInitData = async () => {
      try {
        const [modelsData, constsData] = await Promise.all([
          predictionService.getModelsInfo(),
          dataService.getConstituencies({ limit: 300 }) 
        ]);
        setModels(modelsData);
        setConstituencies(constsData.results || constsData || []);
        
        // Fetch Classification Model Metrics by default
        if (modelsData.classification) {
          const metrics = await predictionService.getModelMetrics('classification');
          setModelMetrics(metrics);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setInitialLoading(false);
      }
    };
    fetchInitData();
    fetchPredictionHistory(1);
  }, []);

  const fetchPredictionHistory = async (page) => {
    try {
      const data = await predictionService.getHistory({ page });
      setPredictionHistory(data.results || data);
      setHistoryTotal(data.count || data.length || 0);
    } catch (err) {
      console.error("Failed to load prediction history");
    }
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    if (!selectedConst) return;

    try {
      setLoading(true);
      setError('');
      setPrediction(null);
      setHistoricalContext(null);
      
      const data = await predictionService.predictConstituency(selectedConst, selectedYear);
      setPrediction(data);

      // Find constituency ID to get historical context
      const constObj = constituencies.find(c => c.name === selectedConst);
      if (constObj) {
        const historyData = await analyticsService.getConstituencyHistory(constObj.id);
        if (historyData && historyData.length > 0) {
          // Assuming array is ordered by year ascending, get the last one
          const latest = historyData.sort((a,b) => b.year - a.year)[0];
          setHistoricalContext(latest);
        }
      }

      // Refresh prediction history log
      fetchPredictionHistory(1);
      setHistoryPage(1);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Prediction feature data not available for this constituency.');
    } finally {
      setLoading(false);
    }
  };

  if (initialLoading) return <Loading />;

  // Prepare feature importance data
  const featureData = modelMetrics?.feature_importance 
    ? Object.entries(modelMetrics.feature_importance)
        .map(([name, val]) => ({ name: name.replace(/_/g, ' '), importance: val }))
        .sort((a, b) => b.importance - a.importance)
        .slice(0, 8)
    : [];

  return (
    <div className="space-y-8">
      <div className="animate-fade-in-up">
        <h1 className="text-3xl font-extrabold text-primary drop-shadow-sm flex items-center">
          <BrainCircuit className="mr-3 text-accent" /> Machine Learning Inference
        </h1>
        <p className="text-secondary text-sm mt-1 font-medium">Estimate constituency-level outcomes using historical election data. Predictions are probabilistic estimates, not factual results.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
        {/* Input Form */}
        <div className="glass-card p-6 col-span-1 h-fit sticky top-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Run Inference</h2>
          <form onSubmit={handlePredict} className="space-y-4">
            <div className="flex gap-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-slate-700 mb-1">Constituency Name</label>
                <input
                  type="text"
                  list="const-list"
                  value={selectedConst}
                  onChange={(e) => setSelectedConst(e.target.value)}
                  placeholder="e.g. Chennai North"
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-accent outline-none"
                  required
                />
                <datalist id="const-list">
                  {constituencies.map((c) => (
                    <option key={c.id} value={c.name} />
                  ))}
                </datalist>
              </div>
              
              <div className="w-1/3">
                <label className="block text-sm font-medium text-slate-700 mb-1">Year</label>
                <select
                  value={selectedYear}
                  onChange={(e) => setSelectedYear(parseInt(e.target.value))}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-accent outline-none bg-white text-slate-800"
                >
                  <option value={2031}>2031</option>
                </select>
              </div>
            </div>
            
            <div className="bg-blue-50 p-3 rounded-lg border border-blue-100 mb-4">
              <p className="text-xs text-blue-800 flex items-start">
                <Target size={14} className="mr-1.5 mt-0.5 flex-shrink-0"/>
                Select a constituency to evaluate historical features through the ML pipeline.
              </p>
            </div>

            <button
              type="submit"
              disabled={loading || !selectedConst}
              className="w-full bg-primary text-white py-2.5 rounded-lg hover:bg-slate-800 transition-colors disabled:opacity-50 flex justify-center items-center font-medium"
            >
              {loading ? <span className="animate-spin h-5 w-5 border-2 border-slate-400 border-t-white rounded-full mr-2" /> : <BrainCircuit size={18} className="mr-2" />}
              {loading ? 'Analyzing historical data...' : 'Generate Prediction'}
            </button>
          </form>

          {error && <div className="mt-4"><ErrorMessage message={error} /></div>}
          
          {/* Explanation Box */}
          <div className="mt-8 border-t border-slate-200 pt-6">
            <h3 className="text-sm font-bold text-primary mb-2">How the prediction works</h3>
            <div className="text-xs text-secondary space-y-2 font-mono bg-slate-50 p-3 rounded-lg border border-slate-200">
              <p>1. Historical Data</p>
              <p className="pl-2">↓ Data cleaning</p>
              <p>2. Feature Engineering</p>
              <p className="pl-2">↓ XGBoost Model</p>
              <p>3. Probability Estimation</p>
            </div>
            <p className="text-[11px] text-slate-400 mt-3 italic">
              Predictions are statistical estimates and do not guarantee actual election outcomes.
            </p>
          </div>
        </div>

        {/* Results View */}
        <div className="col-span-1 lg:col-span-2 flex flex-col gap-6">
          {!prediction && !loading && (
            <div className="bg-slate-50 border border-slate-200 border-dashed rounded-xl h-[400px] flex items-center justify-center text-slate-400">
              Select a constituency and click 'Generate Prediction'
            </div>
          )}
          
          {prediction && !loading && (
            <div className="glass-card p-6 animate-fade-in">
              <div className="flex flex-col md:flex-row justify-between items-start mb-6 pb-6 border-b border-white/20 gap-4">
                <div>
                  <h2 className="text-2xl font-bold text-primary">{prediction.constituency}</h2>
                  <p className="text-secondary font-medium mt-1">Projected Winner (Est. {prediction.election_year})</p>
                </div>
                <div className="bg-slate-50 px-6 py-3 rounded-xl border border-slate-200 text-right">
                  <span className="block text-xs uppercase tracking-wider font-bold text-secondary mb-1">Model-estimated probability</span>
                  <span className="text-4xl font-black text-accent">{prediction.prediction.winner}</span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Probabilities */}
                <div>
                  <h3 className="text-sm font-bold text-slate-700 mb-4 uppercase tracking-wider">Party Win Probabilities</h3>
                  <div className="space-y-4">
                    {Object.entries(prediction.prediction.probabilities)
                      .sort(([, a], [, b]) => b - a)
                      .map(([party, prob]) => (
                      <div key={party}>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="font-semibold text-primary">{party}</span>
                          <span className="text-secondary font-mono">{(prob * 100).toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                          <div 
                            className={`h-full rounded-full transition-all duration-1000 ${party === prediction.prediction.winner ? 'bg-accent' : 'bg-slate-400'}`} 
                            style={{ width: `${Math.min(100, prob * 100)}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Historical Context */}
                <div className="bg-white/40 p-5 rounded-xl border border-white/20">
                  <h3 className="text-sm font-bold text-slate-800 mb-4 uppercase tracking-wider flex items-center">
                    <History size={16} className="mr-2 text-secondary"/> Previous Election Context
                  </h3>
                  {historicalContext ? (
                    <div className="space-y-3">
                      <div className="flex justify-between pb-2 border-b border-slate-200">
                        <span className="text-sm text-secondary">Year</span>
                        <span className="text-sm font-semibold text-primary">{historicalContext.year}</span>
                      </div>
                      <div className="flex justify-between pb-2 border-b border-slate-200">
                        <span className="text-sm text-secondary">Winner</span>
                        <span className="text-sm font-bold text-accent">{historicalContext.party}</span>
                      </div>
                      <div className="flex justify-between pb-2 border-b border-slate-200">
                        <span className="text-sm text-secondary">Vote Share</span>
                        <span className="text-sm font-semibold text-primary">{historicalContext.vote_share.toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-secondary">Winning Margin</span>
                        <span className="text-sm font-semibold text-green-600">+{historicalContext.margin.toLocaleString()}</span>
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm text-secondary">No historical data available for comparison.</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Model Information & Feature Importance */}
          {modelMetrics && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-fade-in">
              <div className="glass-card p-6">
                <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center">
                  <Activity size={18} className="mr-2 text-accent"/> Model Performance
                </h3>
                <div className="mb-4">
                  <p className="text-sm text-secondary"><strong>Model:</strong> {modelMetrics.model_name} (v{modelMetrics.version})</p>
                  <p className="text-sm text-secondary"><strong>Algorithm:</strong> XGBoost Classifier</p>
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm text-left">
                    <thead className="bg-slate-50 text-slate-500 uppercase text-xs font-semibold">
                      <tr>
                        <th className="px-4 py-2 border-b">Metric</th>
                        <th className="px-4 py-2 border-b text-right">Score</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {Object.entries(modelMetrics.metrics).map(([key, value]) => (
                        <tr key={key}>
                          <td className="px-4 py-2 font-medium text-primary capitalize">{key.replace(/_/g, ' ')}</td>
                          <td className="px-4 py-2 text-right font-mono text-secondary">
                            {typeof value === 'number' ? value.toFixed(4) : value}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="glass-card p-6">
                <h3 className="text-lg font-bold text-slate-800 mb-4">Top Feature Importance</h3>
                <p className="text-xs text-secondary mb-4 italic">Features used by the model (does not establish causation).</p>
                <div className="h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={featureData} layout="vertical" margin={{ top: 0, right: 0, left: 20, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#e2e8f0" />
                      <XAxis type="number" hide />
                      <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{fontSize: 10, fill: '#475569'}} width={100} />
                      <Tooltip formatter={(value) => value.toFixed(3)} contentStyle={{borderRadius: '8px', fontSize: '12px'}} cursor={{fill: '#f1f5f9'}} />
                      <Bar dataKey="importance" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}

          {/* Prediction History Log */}
          <div className="glass-card overflow-hidden mt-2 animate-fade-in">
            <div className="px-6 py-4 border-b border-white/20 bg-white/40 flex justify-between items-center">
              <h3 className="font-bold text-slate-800 flex items-center">
                <Clock size={16} className="mr-2"/> Prediction History Log
              </h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-white/20 text-sm">
                <thead className="bg-white/20 text-slate-700 uppercase text-xs font-semibold">
                  <tr>
                    <th className="px-6 py-3 text-left">Timestamp</th>
                    <th className="px-6 py-3 text-left">Constituency</th>
                    <th className="px-6 py-3 text-left">Year</th>
                    <th className="px-6 py-3 text-left">Predicted Winner</th>
                    <th className="px-6 py-3 text-left">Model v.</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {predictionHistory.slice(0, 10).map((log) => (
                    <tr key={log.id} className="hover:bg-slate-50">
                      <td className="px-6 py-3 text-secondary whitespace-nowrap">{new Date(log.prediction_timestamp).toLocaleString()}</td>
                      <td className="px-6 py-3 font-medium text-primary whitespace-nowrap">{log.constituency_name}</td>
                      <td className="px-6 py-3 text-secondary">{log.election_year}</td>
                      <td className="px-6 py-3 font-bold text-accent">{log.predicted_winner_party}</td>
                      <td className="px-6 py-3 text-secondary font-mono">{log.model_version}</td>
                    </tr>
                  ))}
                  {predictionHistory.length === 0 && (
                    <tr>
                      <td colSpan="5" className="px-6 py-6 text-center text-secondary">No predictions run yet.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Predictions;
