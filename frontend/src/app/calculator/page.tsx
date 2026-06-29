"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Upload, FileText } from "lucide-react";
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

export default function CalculatorPage() {
  const router = useRouter();
  const [industry, setIndustry] = useState("");
  const [metrics, setMetrics] = useState<Metrics>({
    electricity_kwh: 0,
    fuel_diesel_liters: 0,
    waste_kg: 0,
    operational_hours: 0,
  });
  const [ocrLoading, setOcrLoading] = useState(false);
  const [ocrResult, setOcrResult] = useState<OcrResponse | null>(null);

  const handleOcrUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setOcrLoading(true);
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
      <h1 className="text-3xl font-bold mb-6">Carbon Calculator</h1>

      <Tabs defaultValue="manual" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="manual">Manual Entry</TabsTrigger>
          <TabsTrigger value="ocr">Upload Invoice</TabsTrigger>
        </TabsList>

        <TabsContent value="manual">
          <Card>
            <CardHeader>
              <CardTitle>Industry & Metrics</CardTitle>
              <CardDescription>
                Select your industry and enter consumption data.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="industry">Industry</Label>
                <Select value={industry} onValueChange={(v) => setIndustry(v ?? "")}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select industry" />
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

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="electricity">Electricity (kWh)</Label>
                  <Input
                    id="electricity"
                    type="number"
                    min="0"
                    value={metrics.electricity_kwh || ""}
                    onChange={(e) =>
                      setMetrics({ ...metrics, electricity_kwh: Number(e.target.value) })
                    }
                    placeholder="0"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="diesel">Diesel (Liters)</Label>
                  <Input
                    id="diesel"
                    type="number"
                    min="0"
                    value={metrics.fuel_diesel_liters || ""}
                    onChange={(e) =>
                      setMetrics({ ...metrics, fuel_diesel_liters: Number(e.target.value) })
                    }
                    placeholder="0"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="waste">Waste (kg)</Label>
                  <Input
                    id="waste"
                    type="number"
                    min="0"
                    value={metrics.waste_kg || ""}
                    onChange={(e) =>
                      setMetrics({ ...metrics, waste_kg: Number(e.target.value) })
                    }
                    placeholder="0"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="hours">Operational Hours</Label>
                  <Input
                    id="hours"
                    type="number"
                    min="0"
                    value={metrics.operational_hours || ""}
                    onChange={(e) =>
                      setMetrics({ ...metrics, operational_hours: Number(e.target.value) })
                    }
                    placeholder="0"
                  />
                </div>
              </div>

              <Button onClick={handleSubmit} disabled={!industry} className="w-full">
                Calculate Emissions
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="ocr">
          <Card>
            <CardHeader>
              <CardTitle>Upload Invoice</CardTitle>
              <CardDescription>
                Upload an electricity bill or fuel invoice (PDF, PNG, JPG) to auto-fill metrics.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="border-2 border-dashed rounded-lg p-8 text-center">
                <Upload className="h-8 w-8 mx-auto mb-4 text-muted-foreground" />
                <Label
                  htmlFor="ocr-upload"
                  className="cursor-pointer text-sm text-muted-foreground hover:text-foreground"
                >
                  {ocrLoading ? "Processing..." : "Click to upload or drag and drop"}
                </Label>
                <Input
                  id="ocr-upload"
                  type="file"
                  accept=".pdf,.png,.jpg,.jpeg"
                  className="hidden"
                  onChange={handleOcrUpload}
                  disabled={ocrLoading}
                />
              </div>

              {ocrResult && (
                <div className="p-4 rounded-lg bg-muted">
                  <div className="flex items-center gap-2 mb-2">
                    <FileText className="h-4 w-4" />
                    <span className="font-medium">
                      {ocrResult.success ? "Extraction Successful" : "Extraction Failed"}
                    </span>
                  </div>
                  {ocrResult.success && ocrResult.extracted_data && (
                    <div className="text-sm space-y-1">
                      <p>Energy: {ocrResult.extracted_data.energy_kwh} kWh</p>
                      <p>Fuel: {ocrResult.extracted_data.fuel_liters} L</p>
                      <p>Cost: ₹{ocrResult.extracted_data.cost}</p>
                      <p>Fuel Type: {ocrResult.extracted_data.fuel_type}</p>
                    </div>
                  )}
                  {ocrResult.error && (
                    <p className="text-sm text-destructive">{ocrResult.error}</p>
                  )}
                </div>
              )}

              {industry && (
                <Button onClick={handleSubmit} className="w-full">
                  Calculate with Extracted Data
                </Button>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
