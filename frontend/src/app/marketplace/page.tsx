"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { IndianRupee, TrendingUp, Clock, Leaf } from "lucide-react";
import { getMarketplaceProjects, type MarketplaceProject } from "@/lib/api";

export default function MarketplacePage() {
  const [projects, setProjects] = useState<MarketplaceProject[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMarketplaceProjects()
      .then(setProjects)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="container py-8 text-center">
        <p className="text-muted-foreground">Loading projects...</p>
      </div>
    );
  }

  return (
    <div className="container py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Project Marketplace</h1>
        <p className="text-muted-foreground mt-1">
          Browse decarbonization projects with ROI, payback, and carbon credit potential.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {projects.map((project) => (
          <Card key={project.id} className="flex flex-col">
            <CardHeader>
              <div className="flex items-start justify-between">
                <CardTitle className="text-lg">{project.title}</CardTitle>
                <Badge variant="secondary">
                  <Leaf className="mr-1 h-3 w-3" />
                  {project.credit_potential} credits
                </Badge>
              </div>
              <CardDescription>{project.description}</CardDescription>
            </CardHeader>
            <CardContent className="mt-auto">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="flex items-center gap-1">
                  <IndianRupee className="h-4 w-4 text-muted-foreground" />
                  <span>₹{project.cost_inr.toLocaleString("en-IN")}</span>
                </div>
                <div className="flex items-center gap-1">
                  <TrendingUp className="h-4 w-4 text-green-600" />
                  <span>{project.roi_pct}% ROI</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span>{project.payback_years} yr payback</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
