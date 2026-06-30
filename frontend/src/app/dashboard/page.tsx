"use client";

import dynamic from "next/dynamic";
import { Card, CardContent, CardDescription, CardHeader } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const Chart = dynamic(() => import("react-apexcharts"), { ssr: false });

const industryBenchmarks = [
  { industry: "Manufacturing", avg_emissions: 45.2, avg_electricity: 55000 },
  { industry: "Textile", avg_emissions: 32.1, avg_electricity: 42000 },
  { industry: "Services", avg_emissions: 18.5, avg_electricity: 28000 },
  { industry: "Retail", avg_emissions: 12.3, avg_electricity: 18000 },
  { industry: "Agriculture", avg_emissions: 22.8, avg_electricity: 35000 },
  { industry: "Education", avg_emissions: 8.7, avg_electricity: 12000 },
  { industry: "Housing", avg_emissions: 6.2, avg_electricity: 9500 },
];

const barChartOptions = {
  chart: {
    type: "bar" as const,
    toolbar: { show: false },
  },
  plotOptions: {
    bar: {
      borderRadius: 4,
      horizontal: true,
    },
  },
  xaxis: {
    categories: industryBenchmarks.map((b) => b.industry),
    title: { text: "tCO2e" },
  },
  title: {
    text: "Average Emissions by Industry (tCO2e)",
    align: "left" as const,
  },
};

const barChartSeries = [
  {
    name: "Avg Emissions",
    data: industryBenchmarks.map((b) => b.avg_emissions),
  },
];

const donutChartOptions = {
  chart: {
    type: "donut" as const,
  },
  labels: ["Scope 1 (Direct)", "Scope 2 (Electricity)", "Scope 3 (Other)"],
  title: {
    text: "Typical Emission Breakdown",
    align: "left" as const,
  },
  plotOptions: {
    pie: {
      donut: {
        size: "65%",
      },
    },
  },
};

const donutChartSeries = [35, 55, 10];

const lineChartOptions = {
  chart: {
    type: "line" as const,
    toolbar: { show: false },
  },
  xaxis: {
    categories: ["2020", "2021", "2022", "2023", "2024", "2025"],
    title: { text: "Year" },
  },
  yaxis: {
    title: { text: "tCO2e" },
  },
  title: {
    text: "Industry Emissions Trend",
    align: "left" as const,
  },
};

const lineChartSeries = [
  {
    name: "Manufacturing",
    data: [52.1, 49.8, 47.2, 45.5, 44.8, 43.2],
  },
  {
    name: "Services",
    data: [22.3, 20.1, 19.2, 18.5, 17.8, 16.9],
  },
  {
    name: "National Avg",
    data: [28.5, 27.2, 26.1, 25.3, 24.8, 24.1],
  },
];

export default function DashboardPage() {
  return (
    <div className="container py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Benchmarking Dashboard</h1>
        <p className="text-muted-foreground mt-1">
          Compare your emissions against industry and regional averages.
        </p>
      </div>

      <Tabs defaultValue="emissions" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="emissions">Emissions</TabsTrigger>
          <TabsTrigger value="breakdown">Breakdown</TabsTrigger>
          <TabsTrigger value="trends">Trends</TabsTrigger>
        </TabsList>

        <TabsContent value="emissions">
          <Card>
            <CardContent className="pt-6">
              <Chart
                options={barChartOptions}
                series={barChartSeries}
                type="bar"
                height={400}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="breakdown">
          <Card>
            <CardContent className="pt-6">
              <div className="flex justify-center">
                <Chart
                  options={donutChartOptions}
                  series={donutChartSeries}
                  type="donut"
                  height={400}
                  width={500}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="trends">
          <Card>
            <CardContent className="pt-6">
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

      <div className="grid gap-6 md:grid-cols-3 mt-6">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Indian MSME Avg</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">24.1 tCO2e</div>
            <p className="text-xs text-muted-foreground">Annual carbon footprint</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Best-in-Class</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">6.2 tCO2e</div>
            <p className="text-xs text-muted-foreground">Housing Societies average</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Reduction Target</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">-45%</div>
            <p className="text-xs text-muted-foreground">India 2030 NDC goal</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
