import React, { useState } from "react";

// Types
interface CarInput {
  make: string;
  model: string;
  year: string;
  mileage: string;
  price: string;
}

interface Listing {
  title: string;
  year: number;
  mileage: number;
  price: number;
  city?: string;
  url?: string;
  engine?: string;
  engine_type?: string;
  engine_size?: string;
  transmission?: string;
  body_type?: string;
  power?: string;
  color?: string;
  doors?: string;
  seats?: string;
  fuel_type?: string;
  seller_type?: string;
  seller_info?: string;
  keywords?: string[];
  score?: number;
  match_quality?: {
    engine_type: boolean;
    transmission: boolean;
    body_type: boolean;
    engine_size: boolean;
    power: boolean;
    color: boolean;
    doors: boolean;
    seats: boolean;
    year: boolean;
    mileage: boolean;
  };
}

interface AnalysisResult {
  average_price: number;
  count_similar: number;
  percent_diff: number;
  is_cheaper: boolean;
  comparison_quality?: string;
  quality_note?: string;
  high_quality_matches?: number;
  medium_quality_matches?: number;
  top_similar?: Listing[];
  sample_titles?: string[];
  error?: string;
}

function App() {
  const [form, setForm] = useState<CarInput>({
    make: "",
    model: "",
    year: "",
    mileage: "",
    price: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setAnalysis(null);

    try {
      // Step 1: Scrape listings
      console.log("Scraping listings...");
      const scrapeRes = await fetch("http://localhost:5000/api/scrape", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          make: form.make,
          model: form.model,
          price_to: Number(form.price),
          pages: 3, // Limit pages for faster response
        }),
      });
      
      if (!scrapeRes.ok) {
        throw new Error(`Failed to scrape listings: ${scrapeRes.status}`);
      }
      
      const listings = await scrapeRes.json();
      console.log(`Found ${listings.length} listings`);

      // Step 2: Analyze the car
      console.log("Analyzing car...");
      const analyzeRes = await fetch("http://localhost:5000/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          input_car: {
            title: `${form.make} ${form.model}`,
            year: Number(form.year),
            mileage: Number(form.mileage),
            price: Number(form.price),
          },
          listings,
        }),
      });
      
      if (!analyzeRes.ok) {
        throw new Error(`Failed to analyze car: ${analyzeRes.status}`);
      }
      
      const result = await analyzeRes.json();
      setAnalysis(result);
      console.log("Analysis complete:", result);
    } catch (err: any) {
      console.error("Error:", err);
      setError(err.message || "An unknown error occurred");
    } finally {
      setLoading(false);
    }
  };

  const getQualityColor = (quality: string) => {
    switch (quality) {
      case 'high': return 'text-green-600';
      case 'medium': return 'text-yellow-600';
      case 'low': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getQualityIcon = (quality: string) => {
    switch (quality) {
      case 'high': return '✅';
      case 'medium': return '⚠️';
      case 'low': return '❌';
      default: return 'ℹ️';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            🚗 Used Car Deal Evaluator
          </h1>
          <p className="text-gray-600">
            Find out if that used car listing is a good deal or not
          </p>
        </div>

        {/* Main Card */}
        <div className="max-w-2xl mx-auto bg-white rounded-2xl shadow-xl p-8">
          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Make
                </label>
                <input
                  type="text"
                  name="make"
                  placeholder="e.g., Opel"
                  value={form.make}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Model
                </label>
                <input
                  type="text"
                  name="model"
                  placeholder="e.g., Corsa"
                  value={form.model}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Year
                </label>
                <input
                  type="number"
                  name="year"
                  placeholder="e.g., 2007"
                  min="1900"
                  max="2030"
                  value={form.year}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Mileage (km)
                </label>
                <input
                  type="number"
                  name="mileage"
                  placeholder="e.g., 150000"
                  min="0"
                  value={form.mileage}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Price (€)
                </label>
                <input
                  type="number"
                  name="price"
                  placeholder="e.g., 2500"
                  min="0"
                  value={form.price}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold py-4 rounded-lg hover:from-blue-700 hover:to-indigo-700 focus:ring-4 focus:ring-blue-300 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Evaluating...
                </div>
              ) : (
                "🚀 Evaluate Deal"
              )}
            </button>
          </form>

          {/* Error Display */}
          {error && (
            <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center">
                <div className="text-red-600 mr-2">⚠️</div>
                <span className="text-red-800">{error}</span>
              </div>
            </div>
          )}

          {/* Results Display */}
          {analysis && (
            <div className="mt-8 space-y-6">
              {analysis.error ? (
                <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div className="flex items-center">
                    <div className="text-yellow-600 mr-2">ℹ️</div>
                    <span className="text-yellow-800">{analysis.error}</span>
                  </div>
                </div>
              ) : (
                <>
                  {/* Main Result */}
                  <div className="text-center p-6 bg-gradient-to-r from-green-50 to-blue-50 rounded-xl border">
                    <div className="text-2xl font-bold mb-2">
                      {analysis.is_cheaper ? (
                        <span className="text-green-600">✅ Good Deal!</span>
                      ) : (
                        <span className="text-red-600">❌ Not a Great Deal</span>
                      )}
                    </div>
                    <div className="text-gray-700">
                      Your car is{" "}
                      <span className="font-bold text-lg">
                        {analysis.percent_diff}%{" "}
                        {analysis.is_cheaper ? "cheaper" : "more expensive"}
                      </span>{" "}
                      than the average of{" "}
                      <span className="font-bold">{analysis.count_similar}</span>{" "}
                      similar listings
                    </div>
                    <div className="mt-2 text-lg font-semibold text-gray-800">
                      Average Price: <span className="text-blue-600">{analysis.average_price}€</span>
                    </div>
                    
                    {/* Comparison Quality */}
                    {analysis.comparison_quality && (
                      <div className="mt-3 p-3 bg-white rounded-lg border">
                        <div className="flex items-center justify-center mb-1">
                          <span className="mr-2">{getQualityIcon(analysis.comparison_quality)}</span>
                          <span className={`font-semibold ${getQualityColor(analysis.comparison_quality)}`}>
                            Comparison Quality: {analysis.comparison_quality.toUpperCase()}
                          </span>
                        </div>
                        {analysis.quality_note && (
                          <div className="text-sm text-gray-600">
                            {analysis.quality_note}
                          </div>
                        )}
                        {analysis.high_quality_matches !== undefined && analysis.medium_quality_matches !== undefined && (
                          <div className="text-xs text-gray-500 mt-1">
                            {analysis.high_quality_matches} high-quality matches, {analysis.medium_quality_matches} medium-quality matches
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Similar Listings */}
                  {analysis.top_similar && analysis.top_similar.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-800 mb-4">
                        📋 Top Similar Listings
                      </h3>
                      <div className="space-y-3">
                        {analysis.top_similar.map((car, idx) => (
                          <div
                            key={car.url || idx}
                            className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
                          >
                            <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                              <div className="flex-1">
                                <div className="font-semibold text-gray-800 mb-1">
                                  {car.title}
                                </div>
                                
                                {/* Basic Info */}
                                <div className="text-sm text-gray-600 space-x-4 mb-2">
                                  <span>📅 {car.year}</span>
                                  <span>🛣️ {car.mileage.toLocaleString()}km</span>
                                  <span className="font-semibold text-green-600">
                                    💰 {car.price}€
                                  </span>
                                  {car.city && <span>📍 {car.city}</span>}
                                </div>
                                
                                {/* Technical Specifications */}
                                <div className="text-sm text-gray-700 space-y-1 mb-2">
                                  {(car.engine_type || car.engine_size || car.transmission || car.body_type || car.power || car.color || car.doors || car.seats) && (
                                    <div className="flex flex-wrap gap-2">
                                      {car.engine_type && (
                                        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                                          ⛽ {car.engine_type}
                                        </span>
                                      )}
                                      {car.engine_size && (
                                        <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs">
                                          🔧 {car.engine_size}L
                                        </span>
                                      )}
                                      {car.transmission && (
                                        <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">
                                          ⚙️ {car.transmission}
                                        </span>
                                      )}
                                      {car.body_type && (
                                        <span className="px-2 py-1 bg-orange-100 text-orange-800 rounded text-xs">
                                          🚗 {car.body_type}
                                        </span>
                                      )}
                                      {car.power && (
                                        <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs">
                                          ⚡ {car.power}
                                        </span>
                                      )}
                                      {car.color && (
                                        <span className="px-2 py-1 bg-pink-100 text-pink-800 rounded text-xs">
                                          🎨 {car.color}
                                        </span>
                                      )}
                                      {car.doors && (
                                        <span className="px-2 py-1 bg-indigo-100 text-indigo-800 rounded text-xs">
                                          🚪 {car.doors}
                                        </span>
                                      )}
                                      {car.seats && (
                                        <span className="px-2 py-1 bg-teal-100 text-teal-800 rounded text-xs">
                                          💺 {car.seats}
                                        </span>
                                      )}
                                    </div>
                                  )}
                                </div>
                                
                                {/* Keywords */}
                                {car.keywords && car.keywords.length > 0 && (
                                  <div className="text-xs text-gray-500 mb-2">
                                    <span className="font-medium">Features:</span> {car.keywords.slice(0, 5).join(', ')}
                                    {car.keywords.length > 5 && ` +${car.keywords.length - 5} more`}
                                  </div>
                                )}
                                
                                {/* Match Quality Indicators */}
                                {car.match_quality && (
                                  <div className="text-xs text-gray-500">
                                    <span className="font-medium">Matches:</span>
                                    <div className="flex flex-wrap gap-1 mt-1">
                                      {car.match_quality.engine_type && (
                                        <span className="px-1 py-0.5 bg-green-100 text-green-700 rounded">Engine</span>
                                      )}
                                      {car.match_quality.transmission && (
                                        <span className="px-1 py-0.5 bg-green-100 text-green-700 rounded">Transmission</span>
                                      )}
                                      {car.match_quality.body_type && (
                                        <span className="px-1 py-0.5 bg-green-100 text-green-700 rounded">Body</span>
                                      )}
                                      {car.match_quality.power && (
                                        <span className="px-1 py-0.5 bg-green-100 text-green-700 rounded">Power</span>
                                      )}
                                      {car.match_quality.engine_size && (
                                        <span className="px-1 py-0.5 bg-blue-100 text-blue-700 rounded">Size</span>
                                      )}
                                      {car.match_quality.color && (
                                        <span className="px-1 py-0.5 bg-blue-100 text-blue-700 rounded">Color</span>
                                      )}
                                      {car.match_quality.doors && (
                                        <span className="px-1 py-0.5 bg-blue-100 text-blue-700 rounded">Doors</span>
                                      )}
                                      {car.match_quality.seats && (
                                        <span className="px-1 py-0.5 bg-blue-100 text-blue-700 rounded">Seats</span>
                                      )}
                                      {car.match_quality.year && (
                                        <span className="px-1 py-0.5 bg-blue-100 text-blue-700 rounded">Year</span>
                                      )}
                                      {car.match_quality.mileage && (
                                        <span className="px-1 py-0.5 bg-blue-100 text-blue-700 rounded">Mileage</span>
                                      )}
                                    </div>
                                  </div>
                                )}
                              </div>
                              
                              {car.url && (
                                <a
                                  href={car.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="mt-2 md:mt-0 md:ml-4 px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
                                >
                                  🔗 View Ad
                                </a>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Sample Titles (fallback) */}
                  {analysis.sample_titles && analysis.sample_titles.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-800 mb-3">
                        📝 Sample Similar Titles
                      </h3>
                      <ul className="space-y-1">
                        {analysis.sample_titles.map((title, i) => (
                          <li key={i} className="text-gray-600 text-sm">
                            • {title}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-gray-500 text-sm">
          <p>© {new Date().getFullYear()} Used Car Deal Evaluator</p>
          <p className="mt-1">Powered by real market data from polovniautomobili.com</p>
        </div>
      </div>
    </div>
  );
}

export default App;
