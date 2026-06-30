"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Upload, FileText, CheckCircle2, ChevronRight, ChevronLeft, Zap, Flame, Trash2, Clock, Factory } from "lucide-react";
import { uploadOcr, type Metrics, type OcrResponse } from "@/lib/api";

const industries = [
  { value: "manufacturing", label: "Manufacturing" },
  { value: "textile", label: "Textile" },
  { value: "services", label: "Services" },
  { value: "retail", label: "Retail" },
  { value: "agriculture", label: "Agriculture" },
  { value: "education", label: "Education (Schools)" },
  { value: "housing", label: "Housing Societies" },
];

const steps = [
  { number: 1, title: "Industry" },
  { number: 2, title: "Energy" },
  { number: 3, title: "Review" },
];

export default function CalculatorPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [industry, setIndustry] = useState("");
  const [metrics, setMetrics] = useState<Metrics>({
    electricity_kwh: 0,
    fuel_diesel_liters: 0,
    waste_kg: 0,
    operational_hours: 0,
  });
  const [ocrLoading, setOcrLoading] = useState(false);
  const [ocrResult, setOcrResult] = useState<OcrResponse | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleOcrUpload = async (file: File) => {
    if (!file) return;

    setOcrLoading(true);
    setOcrResult(null);
    try {
      const result = await uploadOcr(file);
      setOcrResult(result);
      if (result.success && result.extracted_data) {
        const data = result.extracted_data;
        setMetrics((prev) => ({
          ...prev,
          electricity_kwh: data.energy_kwh ?? prev.electricity_kwh,
          fuel_diesel_liters: data.fuel_liters ?? prev.fuel_diesel_liters,
        }));
      }
    } catch (error) {
      console.error("OCR failed:", error);
    } finally {
      setOcrLoading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleOcrUpload(file);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleOcrUpload(file);
  };

  const nextStep = () => {
    if (currentStep < 3) setCurrentStep((prev) => prev + 1);
  };

  const prevStep = () => {
    if (currentStep > 1) setCurrentStep((prev) => prev - 1);
  };

  const handleSubmit = () => {
    if (!industry) return;
    localStorage.setItem(
      "calculatorInput",
      JSON.stringify({ industry, metrics })
    );
    router.push("/calculator/results");
  };

  return (
    <div className="container py-8 max-w-2xl mx-auto">
      {/* Page Title */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-extrabold tracking-tight text-neutral-900 dark:text-neutral-100 mb-2">
          Carbon Footprint Calculator
        </h1>
        <p className="text-neutral-500 dark:text-neutral-400">
          Measure facility emissions and estimate carbon credit potential.
        </p>
      </div>

      {/* Stepper Header */}
      <div className="relative flex justify-between items-center mb-8 max-w-md mx-auto">
        <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-neutral-200 dark:bg-neutral-800 -translate-y-1/2 z-0" />
        
        {steps.map((step) => {
          const isCompleted = currentStep > step.number;
          const isActive = currentStep === step.number;
          
          return (
            <div key={step.number} className="relative z-10 flex flex-col items-center">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center border-2 font-medium text-sm transition-all duration-300 ${
                  isCompleted
                    ? "bg-emerald-600 border-emerald-600 text-white"
                    : isActive
                    ? "bg-white dark:bg-neutral-950 border-emerald-500 text-emerald-600 dark:text-emerald-400 shadow-md shadow-emerald-500/10 scale-105"
                    : "bg-neutral-100 dark:bg-neutral-900 border-neutral-200 dark:border-neutral-800 text-neutral-400"
                }`}
              >
                {isCompleted ? <CheckCircle2 className="h-5 w-5" /> : step.number}
              </div>
              <span
                className={`text-xs mt-2 font-medium transition-colors duration-300 ${
                  isActive
                    ? "text-emerald-600 dark:text-emerald-400 font-bold"
                    : isCompleted
                    ? "text-neutral-800 dark:text-neutral-200"
                    : "text-neutral-400"
                }`}
              >
                {step.title}
              </span>
            </div>
          );
        })}
      </div>

      {/* Step Contents */}
      <div className="mb-8">
        {/* Step 1: Industry Selection */}
        {currentStep === 1 && (
          <Card className="border-neutral-200 dark:border-neutral-800 bg-white/70 dark:bg-neutral-900/50 backdrop-blur-md shadow-lg">
            <CardHeader>
              <CardTitle className="text-xl font-bold flex items-center gap-2">
                <Factory className="h-5 w-5 text-emerald-500" />
                Select Industry Sector
              </CardTitle>
              <CardDescription>
                We use industry benchmarks to tailor your carbon evaluation model.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="industry" className="text-sm font-semibold">
                  Industry Classification
                </Label>
                <Select value={industry} onValueChange={(v) => setIndustry(v ?? "")}>
                  <SelectTrigger className="h-12 border-neutral-300 dark:border-neutral-700 focus:ring-emerald-500 focus:border-emerald-500">
                    <SelectValue placeholder="Select industry sector" />
                  </SelectTrigger>
                  <SelectContent>
                    {industries.map((ind) => (
                      <SelectItem key={ind.value} value={ind.value}>
                        {ind.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 2: Energy & Fuel Metrics */}
        {currentStep === 2 && (
          <div className="space-y-6">
            {/* OCR Invoice Upload Card */}
            <Card className="border-neutral-200 dark:border-neutral-800 bg-white/70 dark:bg-neutral-900/50 backdrop-blur-md">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg font-bold flex items-center gap-2">
                  <Upload className="h-4 w-4 text-emerald-500" />
                  Smart Invoice Auto-fill
                </CardTitle>
                <CardDescription>
                  Upload an energy utility bill or diesel voucher (PDF, PNG, JPG) to extract metrics.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  className={`border-2 border-dashed rounded-xl p-6 text-center transition-all cursor-pointer ${
                    isDragOver
                      ? "border-emerald-500 bg-emerald-500/5"
                      : "border-neutral-300 dark:border-neutral-700 hover:border-emerald-500/50"
                  }`}
                >
                  <Upload className={`h-8 w-8 mx-auto mb-3 transition-colors ${isDragOver ? "text-emerald-500" : "text-neutral-400"}`} />
                  <Label
                    htmlFor="ocr-upload"
                    className="cursor-pointer text-sm font-medium text-neutral-600 dark:text-neutral-300 block mb-1"
                  >
                    {ocrLoading ? "Scanning documents with Gemini AI..." : "Drag & drop file here or click to browse"}
                  </Label>
                  <span className="text-xs text-neutral-400">PDF, PNG, JPG up to 10MB</span>
                  <Input
                    id="ocr-upload"
                    type="file"
                    accept=".pdf,.png,.jpg,.jpeg"
                    className="hidden"
                    onChange={handleFileChange}
                    disabled={ocrLoading}
                  />
                </div>

                {ocrResult && (
                  <div className={`p-4 rounded-lg border ${ocrResult.success ? "bg-emerald-500/5 border-emerald-500/20 text-emerald-800 dark:text-emerald-300" : "bg-red-500/5 border-red-500/20 text-red-800 dark:text-red-300"}`}>
                    <div className="flex items-center gap-2 mb-2">
                      <FileText className="h-4 w-4" />
                      <span className="font-bold text-sm">
                        {ocrResult.success ? "Gemini Extraction Complete!" : "Extraction Failed"}
                      </span>
                    </div>
                    {ocrResult.success && ocrResult.extracted_data ? (
                      <div className="text-xs grid grid-cols-2 gap-2 mt-2 font-medium">
                        <p>💡 Energy: {ocrResult.extracted_data.energy_kwh} kWh</p>
                        <p>⛽ Fuel: {ocrResult.extracted_data.fuel_liters} L</p>
                        <p>💵 Billing period: {ocrResult.extracted_data.billing_period}</p>
                        <p>🏷️ Type: {ocrResult.extracted_data.fuel_type}</p>
                      </div>
                    ) : (
                      <p className="text-xs">{ocrResult.error}</p>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Metrics Form Card */}
            <Card className="border-neutral-200 dark:border-neutral-800 bg-white/70 dark:bg-neutral-900/50 backdrop-blur-md shadow-lg">
              <CardHeader>
                <CardTitle className="text-xl font-bold flex items-center gap-2">
                  <Zap className="h-5 w-5 text-emerald-500" />
                  Consumption Metrics
                </CardTitle>
                <CardDescription>
                  Review and manually adjust your operational metrics.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {/* Electricity */}
                  <div className="space-y-2">
                    <Label htmlFor="electricity" className="text-xs font-semibold flex items-center gap-1.5">
                      <Zap className="h-3.5 w-3.5 text-yellow-500" />
                      Electricity (kWh)
                    </Label>
                    <div className="relative">
                      <Input
                        id="electricity"
                        type="number"
                        min="0"
                        value={metrics.electricity_kwh || ""}
                        onChange={(e) =>
                          setMetrics({ ...metrics, electricity_kwh: Math.max(0, Number(e.target.value)) })
                        }
                        placeholder="0"
                        className="h-11 border-neutral-300 dark:border-neutral-700 focus-visible:ring-emerald-500 focus-visible:border-emerald-500"
                      />
                    </div>
                  </div>

                  {/* Diesel */}
                  <div className="space-y-2">
                    <Label htmlFor="diesel" className="text-xs font-semibold flex items-center gap-1.5">
                      <Flame className="h-3.5 w-3.5 text-orange-500" />
                      Diesel (Liters)
                    </Label>
                    <div className="relative">
                      <Input
                        id="diesel"
                        type="number"
                        min="0"
                        value={metrics.fuel_diesel_liters || ""}
                        onChange={(e) =>
                          setMetrics({ ...metrics, fuel_diesel_liters: Math.max(0, Number(e.target.value)) })
                        }
                        placeholder="0"
                        className="h-11 border-neutral-300 dark:border-neutral-700 focus-visible:ring-emerald-500 focus-visible:border-emerald-500"
                      />
                    </div>
                  </div>

                  {/* Waste */}
                  <div className="space-y-2">
                    <Label htmlFor="waste" className="text-xs font-semibold flex items-center gap-1.5">
                      <Trash2 className="h-3.5 w-3.5 text-neutral-500" />
                      Solid Waste (kg)
                    </Label>
                    <div className="relative">
                      <Input
                        id="waste"
                        type="number"
                        min="0"
                        value={metrics.waste_kg || ""}
                        onChange={(e) =>
                          setMetrics({ ...metrics, waste_kg: Math.max(0, Number(e.target.value)) })
                        }
                        placeholder="0"
                        className="h-11 border-neutral-300 dark:border-neutral-700 focus-visible:ring-emerald-500 focus-visible:border-emerald-500"
                      />
                    </div>
                  </div>

                  {/* Operational Hours */}
                  <div className="space-y-2">
                    <Label htmlFor="hours" className="text-xs font-semibold flex items-center gap-1.5">
                      <Clock className="h-3.5 w-3.5 text-blue-500" />
                      Operational Hours
                    </Label>
                    <div className="relative">
                      <Input
                        id="hours"
                        type="number"
                        min="0"
                        value={metrics.operational_hours || ""}
                        onChange={(e) =>
                          setMetrics({ ...metrics, operational_hours: Math.max(0, Number(e.target.value)) })
                        }
                        placeholder="0"
                        className="h-11 border-neutral-300 dark:border-neutral-700 focus-visible:ring-emerald-500 focus-visible:border-emerald-500"
                      />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Step 3: Review Details */}
        {currentStep === 3 && (
          <Card className="border-neutral-200 dark:border-neutral-800 bg-white/70 dark:bg-neutral-900/50 backdrop-blur-md shadow-lg">
            <CardHeader>
              <CardTitle className="text-xl font-bold flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                Review Verification Details
              </CardTitle>
              <CardDescription>
                Confirm your parameters before calculating carbon credits.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="border border-neutral-200 dark:border-neutral-800 rounded-lg overflow-hidden text-sm">
                <div className="grid grid-cols-2 p-3 bg-neutral-50 dark:bg-neutral-900 border-b border-neutral-200 dark:border-neutral-800">
                  <span className="font-bold text-neutral-600 dark:text-neutral-400">Parameter</span>
                  <span className="font-bold text-neutral-600 dark:text-neutral-400">Value</span>
                </div>
                <div className="grid grid-cols-2 p-3 border-b border-neutral-200 dark:border-neutral-800">
                  <span>Selected Sector</span>
                  <span className="font-semibold capitalize">{industry}</span>
                </div>
                <div className="grid grid-cols-2 p-3 border-b border-neutral-200 dark:border-neutral-800">
                  <span>Electricity Consumption</span>
                  <span className="font-semibold">{metrics.electricity_kwh} kWh</span>
                </div>
                <div className="grid grid-cols-2 p-3 border-b border-neutral-200 dark:border-neutral-800">
                  <span>Diesel Consumption</span>
                  <span className="font-semibold">{metrics.fuel_diesel_liters} Liters</span>
                </div>
                <div className="grid grid-cols-2 p-3 border-b border-neutral-200 dark:border-neutral-800">
                  <span>Facility Solid Waste</span>
                  <span className="font-semibold">{metrics.waste_kg} kg</span>
                </div>
                <div className="grid grid-cols-2 p-3">
                  <span>Weekly Operational Hours</span>
                  <span className="font-semibold">{metrics.operational_hours} Hours</span>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Stepper Footer Controls */}
      <div className="flex justify-between items-center gap-4">
        {currentStep > 1 ? (
          <Button variant="outline" onClick={prevStep} className="h-11 px-6 border-neutral-300 dark:border-neutral-700 flex items-center gap-1.5 cursor-pointer">
            <ChevronLeft className="h-4 w-4" />
            Back
          </Button>
        ) : (
          <div />
        )}

        {currentStep < 3 ? (
          <Button
            onClick={nextStep}
            disabled={currentStep === 1 && !industry}
            className="h-11 px-6 bg-emerald-600 hover:bg-emerald-700 text-white font-medium flex items-center gap-1.5 cursor-pointer"
          >
            Continue
            <ChevronRight className="h-4 w-4" />
          </Button>
        ) : (
          <Button
            onClick={handleSubmit}
            className="h-11 px-8 bg-emerald-600 hover:bg-emerald-700 text-white font-medium flex items-center gap-1.5 shadow-lg shadow-emerald-500/10 cursor-pointer"
          >
            Calculate Emissions
            <CheckCircle2 className="h-4 w-4" />
          </Button>
        )}
      </div>
    </div>
  );
}
