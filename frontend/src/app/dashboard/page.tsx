"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Sparkles, Building } from "lucide-react";
import { calculateScore, type ScoreResponse } from "@/lib/api";

const Chart = dynamic(() => import("react-apexcharts"), { ssr: false });

const industryBenchmarks = [
  { industry: "manufacturing", label: "Manufacturing", avg_emissions: 45.2, avg_electricity: 55000 },
  { industry: "textile", label: "Textile", avg_emissions: 32.1, avg_electricity: 42000 },
  { industry: "services", label: "Services", avg_emissions: 18.5, avg_electricity: 28000 },
  { industry: "retail", label: "Retail", avg_emissions: 12.3, avg_electricity: 18000 },
  { industry: "agriculture", label: "Agriculture", avg_emissions: 22.8, avg_electricity: 35000 },
  { industry: "education", label: "Education", avg_emissions: 8.7, avg_electricity: 12000 },
  { industry: "housing", label: "Housing", avg_emissions: 6.2, avg_electricity: 9500 },
];

export default function DashboardPage() {
  const [userResult, setUserResult] = useState<ScoreResponse | null>(null);
  const [userIndustry, setUserIndustry] = useState<string | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem("calculatorInput");
    if (stored) {
      const parsed = JSON.parse(stored);
      setTimeout(() => {
        setUserIndustry(parsed.industry);
        calculateScore(parsed)
          .then((res) => setUserResult(res))
          .catch((err) => console.error("Failed to load dashboard overlay:", err));
      }, 0);
    }
  }, []);

  // Benchmarks Chart Options
  const barChartOptions = {
    chart: {
      type: "bar" as const,
      toolbar: { show: false },
      fontFamily: "Inter, sans-serif",
    },
    colors: ["#10b981"],
    plotOptions: {
      bar: {
        borderRadius: 5,
        horizontal: true,
        barHeight: "50%",
      },
    },
    xaxis: {
      categories: industryBenchmarks.map((b) => b.label),
      labels: {
        style: { colors: "#888" },
      },
    },
    yaxis: {
      labels: {
        style: { colors: "#888" },
      },
    },
    grid: {
      borderColor: "#f1f1f1",
    },
    dataLabels: {
      enabled: true,
      formatter: (val: number) => `${val} tCO2e`,
    },
  };

  const barChartSeries = [
    {
      name: "Sector Average Footprint",
      data: industryBenchmarks.map((b) => b.avg_emissions),
    },
  ];

  // Breakdown Chart Options
  // Default values or user-specific values
  const userScope1 = userResult?.scope_1_emissions_tco2e ?? 12.5;
  const userScope2 = userResult?.scope_2_emissions_tco2e ?? 22.1;
  const userScope3 = (userResult as unknown as { scope_3_emissions_tco2e?: number })?.scope_3_emissions_tco2e ?? 3.5;

  const donutChartOptions = {
    chart: {
      type: "donut" as const,
      fontFamily: "Inter, sans-serif",
    },
    colors: ["#10b981", "#3b82f6", "#6366f1"],
    labels: ["Scope 1 (Direct Fuels)", "Scope 2 (Electricity)", "Scope 3 (Waste & Logistics)"],
    plotOptions: {
      pie: {
        donut: {
          size: "70%",
          labels: {
            show: true,
            total: {
              show: true,
              label: "Total Emissions",
              formatter: () => `${userResult?.total_emissions_tco2e ?? 38.1} tCO2e`,
            },
          },
        },
      },
    },
    legend: {
      position: "bottom" as const,
      labels: { colors: "#888" },
    },
  };

  const donutChartSeries = [userScope1, userScope2, userScope3];

  // Projection Trend Chart
  const lineChartOptions = {
    chart: {
      type: "line" as const,
      toolbar: { show: false },
      fontFamily: "Inter, sans-serif",
    },
    colors: ["#10b981", "#6366f1", "#f59e0b"],
    stroke: {
      curve: "smooth" as const,
      width: 3,
    },
    xaxis: {
      categories: ["2026", "2027", "2028", "2029", "2030"],
      labels: { style: { colors: "#888" } },
    },
    yaxis: {
      labels: { style: { colors: "#888" } },
    },
    grid: {
      borderColor: "#f1f1f1",
    },
  };

  const lineChartSeries = [
    {
      name: "Your Projected Decarbonization Pathway",
      data: [
        userResult?.total_emissions_tco2e ?? 38.1,
        (userResult?.total_emissions_tco2e ?? 38.1) * 0.9,
        (userResult?.total_emissions_tco2e ?? 38.1) * 0.75,
        (userResult?.total_emissions_tco2e ?? 38.1) * 0.62,
        (userResult?.total_emissions_tco2e ?? 38.1) * 0.50,
      ],
    },
    {
      name: "National Average Pathway",
      data: [28.5, 27.2, 26.1, 24.8, 23.5],
    },
    {
      name: "India 2030 NDC Target Line",
      data: [35.0, 31.0, 27.0, 23.0, 19.0],
    },
  ];

  // Calculate sector benchmark comparison
  const matchedBenchmark = industryBenchmarks.find((b) => b.industry === userIndustry);
  const benchmarkVal = matchedBenchmark ? matchedBenchmark.avg_emissions : 24.1;
  const userEmissionsVal = userResult ? userResult.total_emissions_tco2e : 0;
  const isLower = userEmissionsVal < benchmarkVal;
  const pctDiff = benchmarkVal > 0 ? Math.abs(((userEmissionsVal - benchmarkVal) / benchmarkVal) * 100).toFixed(0) : "0";

  return (
    <div className="container py-8 max-w-6xl mx-auto space-y-8">
      {/* Title */}
      <div>
        <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border border-emerald-500/20 bg-emerald-500/5 text-emerald-600 dark:text-emerald-400 text-xs font-semibold mb-3">
          <Sparkles className="h-3 w-3" />
          <span>Interactive Benchmarking</span>
        </div>
        <h1 className="text-3xl font-extrabold tracking-tight text-neutral-900 dark:text-neutral-100">
          Benchmarking Dashboard
        </h1>
        <p className="text-neutral-500 dark:text-neutral-400 text-sm mt-1">
          Evaluate facility performance indicators against regional sectors and national carbon targets.
        </p>
      </div>

      {/* User Data Overlay Section */}
      {userResult && (
        <Card className="border border-emerald-500/20 bg-emerald-500/5 backdrop-blur-md">
          <CardHeader className="p-6 pb-2">
            <CardTitle className="text-base font-bold text-emerald-800 dark:text-emerald-300 flex items-center gap-2">
              <Building className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
              Active Facility Benchmark Overlay
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6 pt-0">
            <p className="text-sm text-neutral-700 dark:text-neutral-300 leading-relaxed font-medium">
              Your facility emits <span className="font-bold text-emerald-700 dark:text-emerald-400">{userEmissionsVal} tCO2e</span>. 
              This is <span className="font-bold text-emerald-700 dark:text-emerald-400">{pctDiff}% {isLower ? "lower" : "higher"}</span> than the 
              average <span className="capitalize font-bold">{userIndustry}</span> facility average of <span className="font-bold">{benchmarkVal} text tCO2e</span>.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Grid: Benchmark stats */}
      <div className="grid gap-6 md:grid-cols-3">
        <Card className="border-neutral-200 dark:border-neutral-800 bg-white/70 dark:bg-neutral-900/50 backdrop-blur-md">
          <CardHeader className="p-5 pb-2">
            <CardDescription className="text-xs font-bold text-neutral-500 dark:text-neutral-400">Indian MSME Sector Avg</CardDescription>
          </CardHeader>
          <CardContent className="p-5 pt-0">
            <div className="text-2xl font-extrabold text-neutral-800 dark:text-neutral-100">24.1 <span className="text-sm font-normal text-neutral-450">tCO2e/yr</span></div>
            <p className="text-[10px] text-neutral-450 mt-1">BEE benchmark baseline</p>
          </CardContent>
        </Card>
        <Card className="border-neutral-200 dark:border-neutral-800 bg-white/70 dark:bg-neutral-900/50 backdrop-blur-md">
          <CardHeader className="p-5 pb-2">
            <CardDescription className="text-xs font-bold text-neutral-500 dark:text-neutral-400">Best-in-Class Sector</CardDescription>
          </CardHeader>
          <CardContent className="p-5 pt-0">
            <div className="text-2xl font-extrabold text-neutral-800 dark:text-neutral-100">6.2 <span className="text-sm font-normal text-neutral-450">tCO2e/yr</span></div>
            <p className="text-[10px] text-neutral-450 mt-1">Housing & services base rate</p>
          </CardContent>
        </Card>
        <Card className="border-neutral-200 dark:border-neutral-800 bg-emerald-500/5 dark:bg-emerald-500/10 border-emerald-500/20">
          <CardHeader className="p-5 pb-2">
            <CardDescription className="text-xs font-bold text-emerald-600 dark:text-emerald-400">Decarbonization Target</CardDescription>
          </CardHeader>
          <CardContent className="p-5 pt-0">
            <div className="text-2xl font-extrabold text-emerald-700 dark:text-emerald-300">-45% <span className="text-sm font-normal text-emerald-500">Reduction</span></div>
            <p className="text-[10px] text-emerald-600/70 mt-1">India NDC carbon timeline</p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs of Charts */}
      <Tabs defaultValue="emissions" className="w-full">
        <TabsList className="grid w-full grid-cols-3 max-w-md mx-auto mb-6 p-1 border border-neutral-200 dark:border-neutral-800 bg-white/50 dark:bg-neutral-950/20 rounded-lg">
          <TabsTrigger value="emissions" className="cursor-pointer">Sector Comparisons</TabsTrigger>
          <TabsTrigger value="breakdown" className="cursor-pointer">Scope Breakdowns</TabsTrigger>
          <TabsTrigger value="trends" className="cursor-pointer">5-Year Pathways</TabsTrigger>
        </TabsList>

        {/* Sector Comparison Bar Chart */}
        <TabsContent value="emissions">
          <Card className="border-neutral-200 dark:border-neutral-800 bg-white/70 dark:bg-neutral-900/50 backdrop-blur-md p-6">
            <CardContent className="p-0">
              <Chart
                options={barChartOptions}
                series={barChartSeries}
                type="bar"
                height={400}
              />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Scope Breakdowns Donut Chart */}
        <TabsContent value="breakdown">
          <Card className="border-neutral-200 dark:border-neutral-800 bg-white/70 dark:bg-neutral-900/50 backdrop-blur-md p-6">
            <CardContent className="p-0 flex justify-center items-center">
              <div className="w-full max-w-lg">
                <Chart
                  options={donutChartOptions}
                  series={donutChartSeries}
                  type="donut"
                  height={380}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 5-Year Trends Line Chart */}
        <TabsContent value="trends">
          <Card className="border-neutral-200 dark:border-neutral-800 bg-white/70 dark:bg-neutral-900/50 backdrop-blur-md p-6">
            <CardContent className="p-0">
              <Chart
                options={lineChartOptions}
                series={lineChartSeries}
                type="line"
                height={400}
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
