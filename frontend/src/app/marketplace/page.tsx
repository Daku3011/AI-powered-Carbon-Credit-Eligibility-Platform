import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { IndianRupee, TrendingUp, Clock, Leaf, Sparkles } from "lucide-react";
import { getMarketplaceProjects } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function MarketplacePage() {
  const projects = await getMarketplaceProjects().catch(() => []);

  return (
    <div className="container py-8 max-w-6xl mx-auto space-y-8">
      {/* Background ambient lighting */}
      <div className="absolute top-10 right-10 w-[300px] h-[300px] bg-emerald-500/5 rounded-full blur-[100px] pointer-events-none" />

      {/* Header */}
      <div className="relative z-10">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border border-emerald-500/20 bg-emerald-500/5 text-emerald-600 dark:text-emerald-400 text-xs font-semibold mb-3">
          <Sparkles className="h-3 w-3" />
          <span>Decarbonization Transitions</span>
        </div>
        <h1 className="text-3xl font-extrabold tracking-tight text-neutral-900 dark:text-neutral-100">
          Clean Technology Marketplace
        </h1>
        <p className="text-neutral-500 dark:text-neutral-400 text-sm mt-1">
          Explore structured capital equipment retrofits and transition paths with certified carbon offsets potential.
        </p>
      </div>

      {/* Projects Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {projects.map((project) => {
          // Dynamically set accents based on roi
          const isHighRoi = project.roi_pct >= 25;
          
          return (
            <Card key={project.id} className="group relative flex flex-col border border-neutral-200 dark:border-neutral-800 bg-white/70 dark:bg-neutral-900/50 backdrop-blur-md transition-all duration-300 hover:-translate-y-1.5 hover:border-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/5 cursor-pointer overflow-hidden">
              {/* Header Glow accent */}
              <div className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${isHighRoi ? "from-emerald-500 to-teal-500" : "from-blue-500 to-indigo-500"} opacity-70`} />

              <CardHeader className="p-6">
                <div className="flex items-start justify-between gap-4 mb-3">
                  <Badge variant="outline" className={`text-[10px] font-bold px-2 py-0.5 rounded-md border ${
                    isHighRoi 
                      ? "bg-emerald-500/5 border-emerald-500/20 text-emerald-600 dark:text-emerald-400" 
                      : "bg-blue-500/5 border-blue-500/20 text-blue-600 dark:text-blue-400"
                  }`}>
                    {isHighRoi ? "High Yield" : "Standard Retfit"}
                  </Badge>
                  <Badge variant="outline" className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-neutral-100 dark:bg-neutral-800 border-neutral-200 dark:border-neutral-700 text-neutral-600 dark:text-neutral-400 flex items-center gap-1">
                    <Leaf className="h-2.5 w-2.5 text-emerald-500" />
                    {project.credit_potential} tCO2e/yr
                  </Badge>
                </div>
                
                <CardTitle className="text-lg font-bold text-neutral-800 dark:text-neutral-100 group-hover:text-emerald-500 transition-colors">
                  {project.title}
                </CardTitle>
                <CardDescription className="text-neutral-500 dark:text-neutral-400 text-xs mt-2 leading-relaxed h-16 overflow-hidden">
                  {project.description}
                </CardDescription>
              </CardHeader>

              <CardContent className="p-6 pt-0 mt-auto border-t border-neutral-100 dark:border-neutral-800/80 bg-neutral-50/30 dark:bg-neutral-900/10">
                <div className="grid grid-cols-3 gap-3 pt-4 text-xs font-semibold">
                  <div className="space-y-1">
                    <span className="text-[10px] text-neutral-400 font-bold block">Est. Cost</span>
                    <div className="flex items-center gap-0.5 text-neutral-850 dark:text-neutral-200">
                      <IndianRupee className="h-3 w-3 text-neutral-550" />
                      <span>₹{project.cost_inr.toLocaleString("en-IN")}</span>
                    </div>
                  </div>
                  <div className="space-y-1">
                    <span className="text-[10px] text-neutral-400 font-bold block">Return ROI</span>
                    <div className="flex items-center gap-0.5 text-emerald-600 dark:text-emerald-400">
                      <TrendingUp className="h-3 w-3" />
                      <span>{project.roi_pct}%</span>
                    </div>
                  </div>
                  <div className="space-y-1">
                    <span className="text-[10px] text-neutral-400 font-bold block">Payback</span>
                    <div className="flex items-center gap-0.5 text-neutral-850 dark:text-neutral-200">
                      <Clock className="h-3 w-3 text-neutral-550" />
                      <span>{project.payback_years} yrs</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
