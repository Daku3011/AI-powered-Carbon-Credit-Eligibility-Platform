"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Download, TrendingDown, Leaf, IndianRupee, Activity, Calendar } from "lucide-react";
import { calculateScore, exportReport, type ScoreRequest, type ScoreResponse } from "@/lib/api";

export default function CalculatorResultsPage() {
  const [result, setResult] = useState<ScoreResponse | null>(null);
  const [input, setInput] = useState<ScoreRequest | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [exporting, setExporting] = useState<"pdf" | "xlsx" | null>(null);

  const handleExport = async (format: "pdf" | "xlsx") => {
    if (!result || !input) return;
    setExporting(format);
    try {
      const blob = await exportReport(
        {
          ...input,
          eligibility_score: result.eligibility_score,
          roadmap: result.roadmap,
        },
        format
      );
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `carbon_report.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Export failed:", err);
    } finally {
      setExporting(null);
    }
  };

  useEffect(() => {
    const stored = localStorage.getItem("calculatorInput");
    if (!stored) {
      setTimeout(() => setLoading(false), 0);
      return;
    }

    const parsed = JSON.parse(stored) as ScoreRequest;
    setTimeout(() => {
      setInput(parsed);
      calculateScore(parsed)
        .then((res) => setResult(res))
        .catch((err) => setError(err.message))
        .finally(() => setLoading(false));
    }, 0);
  }, []);

  if (loading) {
    return (
      <div className="container py-8 text-center max-w-lg mx-auto py-32 space-y-4">
        <div className="w-12 h-12 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-neutral-500 dark:text-neutral-400 font-medium">Analyzing facility footprint and generating Decarbonization model...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container py-8 text-center max-w-md mx-auto py-32 space-y-4">
        <p className="text-red-500 font-bold">Calculation Failed</p>
        <p className="text-sm text-neutral-500">{error}</p>
        <Link href="/calculator">
          <Button variant="outline" className="cursor-pointer">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Calculator
          </Button>
        </Link>
      </div>
    );
  }

  if (!result || !input) {
    return (
      <div className="container py-8 text-center max-w-md mx-auto py-32 space-y-4">
        <p className="text-neutral-500 dark:text-neutral-400 mb-4">No active calculation record found.</p>
        <Link href="/calculator">
          <Button className="cursor-pointer">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Start New Calculation
          </Button>
        </Link>
      </div>
    );
  }

  const { eligibility_score: score, roadmap } = result;

  // Extract scope_3 if present in result, or default to 0.0
  const scope_3 = (result as unknown as { scope_3_emissions_tco2e?: number }).scope_3_emissions_tco2e ?? 0.0;

  return (
    <div className="container py-8 max-w-4xl mx-auto space-y-8">
      {/* Header controls */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-neutral-200 dark:border-neutral-800 pb-6">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-neutral-900 dark:text-neutral-100">
            Calculation Results
          </h1>
          <p className="text-neutral-500 dark:text-neutral-400 text-sm">
            Audited results for your {input.industry} facility.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button
            variant="outline"
            onClick={() => handleExport("pdf")}
            disabled={exporting === "pdf"}
            className="cursor-pointer border-neutral-300 dark:border-neutral-700 h-10 px-4 flex items-center gap-1.5"
          >
            <Download className="h-4 w-4" />
            {exporting === "pdf" ? "Generating PDF..." : "Export PDF"}
          </Button>
          <Button
            variant="outline"
            onClick={() => handleExport("xlsx")}
            disabled={exporting === "xlsx"}
            className="cursor-pointer border-neutral-300 dark:border-neutral-700 h-10 px-4 flex items-center gap-1.5"
          >
            <Download className="h-4 w-4" />
            {exporting === "xlsx" ? "Generating Sheet..." : "Export Excel"}
          </Button>
          <Link href="/calculator">
            <Button variant="outline" className="cursor-pointer border-neutral-300 dark:border-neutral-700 h-10 px-4">
              <ArrowLeft className="mr-1.5 h-4 w-4" />
              New Run
            </Button>
          </Link>
        </div>
      </div>

      {/* Grid of Emissions */}
      <div>
        <h2 className="text-lg font-bold text-neutral-800 dark:text-neutral-200 mb-4 flex items-center gap-2">
          <Activity className="h-5 w-5 text-emerald-500" />
          Carbon Footprint Breakdown
        </h2>
        <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
          <Card className="border-neutral-200 dark:border-neutral-800 bg-white/70 dark:bg-neutral-900/50 backdrop-blur-md">
            <CardHeader className="p-4 pb-2">
              <CardDescription className="text-xs font-semibold text-neutral-500 dark:text-neutral-400">Scope 1 (Direct)</CardDescription>
            </CardHeader>
            <CardContent className="p-4 pt-0">
              <div className="text-xl font-bold text-neutral-800 dark:text-neutral-100">{result.scope_1_emissions_tco2e} <span className="text-xs font-normal text-neutral-400">tCO2e</span></div>
              <p className="text-[10px] text-neutral-400 mt-1">Diesel & fuel combustion</p>
            </CardContent>
          </Card>
          <Card className="border-neutral-200 dark:border-neutral-800 bg-white/70 dark:bg-neutral-900/50 backdrop-blur-md">
            <CardHeader className="p-4 pb-2">
              <CardDescription className="text-xs font-semibold text-neutral-500 dark:text-neutral-400">Scope 2 (Indirect)</CardDescription>
            </CardHeader>
            <CardContent className="p-4 pt-0">
              <div className="text-xl font-bold text-neutral-800 dark:text-neutral-100">{result.scope_2_emissions_tco2e} <span className="text-xs font-normal text-neutral-400">tCO2e</span></div>
              <p className="text-[10px] text-neutral-400 mt-1">Purchased grid electricity</p>
            </CardContent>
          </Card>
          <Card className="border-neutral-200 dark:border-neutral-800 bg-white/70 dark:bg-neutral-900/50 backdrop-blur-md">
            <CardHeader className="p-4 pb-2">
              <CardDescription className="text-xs font-semibold text-neutral-500 dark:text-neutral-400">Scope 3 (Waste)</CardDescription>
            </CardHeader>
            <CardContent className="p-4 pt-0">
              <div className="text-xl font-bold text-neutral-800 dark:text-neutral-100">{scope_3} <span className="text-xs font-normal text-neutral-400">tCO2e</span></div>
              <p className="text-[10px] text-neutral-400 mt-1">Solid waste landfill methane</p>
            </CardContent>
          </Card>
          <Card className="border-neutral-200 dark:border-neutral-800 bg-emerald-500/5 dark:bg-emerald-500/10 border-emerald-500/20">
            <CardHeader className="p-4 pb-2">
              <CardDescription className="text-xs font-semibold text-emerald-600 dark:text-emerald-400">Total Footprint</CardDescription>
            </CardHeader>
            <CardContent className="p-4 pt-0">
              <div className="text-xl font-bold text-emerald-700 dark:text-emerald-300">{result.total_emissions_tco2e} <span className="text-xs font-normal text-emerald-500">tCO2e</span></div>
              <p className="text-[10px] text-emerald-500/70 mt-1">Combined facility footprint</p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Eligibility Score Details */}
      <Card className="border-neutral-200 dark:border-neutral-800 bg-white/70 dark:bg-neutral-900/50 backdrop-blur-md shadow-md">
        <CardHeader>
          <CardTitle className="text-lg font-bold flex items-center gap-2">
            <Leaf className="h-5 w-5 text-emerald-500" />
            AI eligibility & Credits Valuation
          </CardTitle>
          <CardDescription>Estimated potential under voluntary carbon registries.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 grid-cols-2 md:grid-cols-3 text-sm">
            <div className="space-y-1">
              <span className="text-neutral-500 text-xs font-semibold block">Readiness Score</span>
              <div className="flex items-baseline gap-1.5">
                <span className="text-2xl font-bold">{score.readiness_score}</span>
                <span className="text-neutral-400 text-xs">/100</span>
              </div>
            </div>
            <div className="space-y-1">
              <span className="text-neutral-500 text-xs font-semibold block">Emissions Rating</span>
              <Badge
                variant="outline"
                className={`text-xs font-bold px-2 py-0.5 border ${
                  score.emissions_rating === "High"
                    ? "bg-red-500/5 border-red-500/30 text-red-600"
                    : score.emissions_rating === "Medium"
                    ? "bg-amber-500/5 border-amber-500/30 text-amber-600"
                    : "bg-emerald-500/5 border-emerald-500/30 text-emerald-600"
                }`}
              >
                {score.emissions_rating}
              </Badge>
            </div>
            <div className="space-y-1">
              <span className="text-neutral-500 text-xs font-semibold block">Reduction Potential</span>
              <div className="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400">
                <TrendingDown className="h-4 w-4" />
                <span className="text-2xl font-bold">{score.reduction_potential_pct}%</span>
              </div>
            </div>
            <div className="space-y-1">
              <span className="text-neutral-500 text-xs font-semibold block">Annual Offset Credits</span>
              <div className="flex items-baseline gap-1.5 text-neutral-800 dark:text-neutral-200">
                <span className="text-2xl font-bold">{score.carbon_credit_potential}</span>
                <span className="text-neutral-400 text-xs">Credits/yr</span>
              </div>
            </div>
            <div className="space-y-1">
              <span className="text-neutral-500 text-xs font-semibold block">Projected Revenue</span>
              <div className="flex items-baseline gap-1 text-emerald-600 dark:text-emerald-400">
                <IndianRupee className="h-3.5 w-3.5" />
                <span className="text-2xl font-bold">
                  {score.projected_revenue_inr.toLocaleString("en-IN")}
                </span>
              </div>
            </div>
            <div className="space-y-1">
              <span className="text-neutral-500 text-xs font-semibold block">Verification Confidence</span>
              <span className="text-2xl font-bold">{(score.confidence_score * 100).toFixed(0)}%</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stepper Roadmap */}
      <div>
        <h2 className="text-lg font-bold text-neutral-800 dark:text-neutral-200 mb-6 flex items-center gap-2">
          <Calendar className="h-5 w-5 text-emerald-500" />
          Decarbonization Roadmap
        </h2>
        <div className="relative border-l-2 border-neutral-200 dark:border-neutral-800 pl-6 ml-4 space-y-6">
          {roadmap.map((item) => (
            <div key={item.year} className="relative">
              {/* Step circle indicator */}
              <div className="absolute -left-[37px] top-1 w-6 h-6 rounded-full bg-emerald-600 border-4 border-white dark:border-neutral-950 flex items-center justify-center text-[10px] font-bold text-white shadow-md">
                {item.year}
              </div>
              
              <Card className="border-neutral-200 dark:border-neutral-800 bg-white/50 dark:bg-neutral-900/30 backdrop-blur-sm">
                <CardHeader className="p-4 pb-2">
                  <CardTitle className="text-base font-bold text-neutral-800 dark:text-neutral-200">
                    {item.recommendation}
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-4 pt-0 text-xs">
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-neutral-500 dark:text-neutral-400 mt-2 font-medium">
                    <div className="flex items-center gap-1">
                      <span className="text-neutral-400">Capital Investment:</span>
                      <span className="text-neutral-700 dark:text-neutral-300">₹{item.investment_inr.toLocaleString("en-IN")}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="text-neutral-400">Operational Savings:</span>
                      <span className="text-neutral-700 dark:text-neutral-300">₹{item.savings_inr.toLocaleString("en-IN")}/yr</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="text-neutral-400">Estimated Carbon Offset:</span>
                      <span className="text-emerald-600 dark:text-emerald-400 font-bold">{item.credits_earned} Credits/yr</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
