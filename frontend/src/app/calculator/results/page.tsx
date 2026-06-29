"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ArrowLeft, Download, TrendingDown, Leaf, IndianRupee } from "lucide-react";
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
      setLoading(false);
      return;
    }

    const parsed = JSON.parse(stored) as ScoreRequest;
    setInput(parsed);

    calculateScore(parsed)
      .then(setResult)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="container py-8 text-center">
        <p className="text-muted-foreground">Calculating emissions...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container py-8 text-center">
        <p className="text-destructive mb-4">Error: {error}</p>
        <Link href="/calculator">
          <Button variant="outline">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Calculator
          </Button>
        </Link>
      </div>
    );
  }

  if (!result || !input) {
    return (
      <div className="container py-8 text-center">
        <p className="text-muted-foreground mb-4">No calculation data found.</p>
        <Link href="/calculator">
          <Button>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Start New Calculation
          </Button>
        </Link>
      </div>
    );
  }

  const { eligibility_score: score, roadmap } = result;

  return (
    <div className="container py-8 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Results</h1>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => handleExport("pdf")}
            disabled={exporting === "pdf"}
          >
            <Download className="mr-2 h-4 w-4" />
            {exporting === "pdf" ? "Exporting..." : "Export PDF"}
          </Button>
          <Button
            variant="outline"
            onClick={() => handleExport("xlsx")}
            disabled={exporting === "xlsx"}
          >
            <Download className="mr-2 h-4 w-4" />
            {exporting === "xlsx" ? "Exporting..." : "Export Excel"}
          </Button>
          <Link href="/calculator">
            <Button variant="outline">
              <ArrowLeft className="mr-2 h-4 w-4" />
              New Calculation
            </Button>
          </Link>
        </div>
      </div>

      {/* Emissions Summary */}
      <div className="grid gap-4 md:grid-cols-3 mb-6">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Scope 1 Emissions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{result.scope_1_emissions_tco2e} tCO2e</div>
            <p className="text-xs text-muted-foreground">Direct emissions (fuel combustion)</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Scope 2 Emissions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{result.scope_2_emissions_tco2e} tCO2e</div>
            <p className="text-xs text-muted-foreground">Indirect emissions (electricity)</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total Emissions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{result.total_emissions_tco2e} tCO2e</div>
            <p className="text-xs text-muted-foreground">Combined carbon footprint</p>
          </CardContent>
        </Card>
      </div>

      {/* Eligibility Score */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>AI Eligibility Score</CardTitle>
          <CardDescription>Your readiness for carbon credit monetization</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Readiness Score</p>
              <div className="flex items-center gap-2">
                <span className="text-3xl font-bold">{score.readiness_score}</span>
                <span className="text-muted-foreground">/100</span>
              </div>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Emissions Rating</p>
              <Badge
                variant={
                  score.emissions_rating === "High"
                    ? "destructive"
                    : score.emissions_rating === "Medium"
                    ? "default"
                    : "secondary"
                }
              >
                {score.emissions_rating}
              </Badge>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Reduction Potential</p>
              <div className="flex items-center gap-1">
                <TrendingDown className="h-4 w-4 text-green-600" />
                <span className="text-2xl font-bold">{score.reduction_potential_pct}%</span>
              </div>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Carbon Credit Potential</p>
              <div className="flex items-center gap-1">
                <Leaf className="h-4 w-4 text-green-600" />
                <span className="text-2xl font-bold">{score.carbon_credit_potential}</span>
                <span className="text-muted-foreground">credits</span>
              </div>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Projected Revenue</p>
              <div className="flex items-center gap-1">
                <IndianRupee className="h-4 w-4" />
                <span className="text-2xl font-bold">
                  {score.projected_revenue_inr.toLocaleString("en-IN")}
                </span>
              </div>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Confidence Score</p>
              <span className="text-2xl font-bold">{(score.confidence_score * 100).toFixed(0)}%</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Roadmap */}
      <Card>
        <CardHeader>
          <CardTitle>Carbon Reduction Roadmap</CardTitle>
          <CardDescription>Your multi-year implementation plan</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {roadmap.map((item) => (
              <div
                key={item.year}
                className="flex items-start gap-4 p-4 rounded-lg border"
              >
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-medium">
                  Y{item.year}
                </div>
                <div className="flex-1">
                  <p className="font-medium">{item.recommendation}</p>
                  <div className="flex gap-4 mt-2 text-sm text-muted-foreground">
                    <span>Investment: ₹{item.investment_inr.toLocaleString("en-IN")}</span>
                    <span>Savings: ₹{item.savings_inr.toLocaleString("en-IN")}/yr</span>
                    <span>Credits: {item.credits_earned}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
