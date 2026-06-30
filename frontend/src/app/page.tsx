import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Calculator, BarChart3, MessageSquare, Store, ArrowRight, ShieldCheck } from "lucide-react";

const features = [
  {
    title: "Carbon Calculator",
    description: "Measure Scope 1, 2 & 3 emissions with instant carbon credit eligibility scoring.",
    href: "/calculator",
    icon: Calculator,
    color: "text-emerald-500",
    bg: "bg-emerald-500/5 dark:bg-emerald-500/10",
  },
  {
    title: "Project Marketplace",
    description: "Discover clean-tech solutions with guaranteed ROI, payback periods, and credit offsets.",
    href: "/marketplace",
    icon: Store,
    color: "text-blue-500",
    bg: "bg-blue-500/5 dark:bg-blue-500/10",
  },
  {
    title: "Benchmarking Dashboard",
    description: "Compare your operational metrics against regional and sector-specific averages.",
    href: "/dashboard",
    icon: BarChart3,
    color: "text-indigo-500",
    bg: "bg-indigo-500/5 dark:bg-indigo-500/10",
  },
  {
    title: "AI Carbon Consultant",
    description: "Consult our Gemini-powered specialist on compliance, ICM registration, and Bureau of Energy Efficiency (BEE) guidelines.",
    href: "/chatbot",
    icon: MessageSquare,
    color: "text-teal-500",
    bg: "bg-teal-500/5 dark:bg-teal-500/10",
  },
];

export default function Home() {
  return (
    <div className="relative overflow-hidden min-h-screen py-16 flex flex-col items-center justify-center">
      {/* Background ambient light */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-emerald-500/10 dark:bg-emerald-500/5 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-10 left-10 w-[300px] h-[300px] bg-blue-500/10 dark:bg-blue-500/5 rounded-full blur-[100px] pointer-events-none" />

      <div className="relative z-10 container max-w-5xl mx-auto px-4 text-center">
        {/* Badge */}
        <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/5 text-emerald-600 dark:text-emerald-400 text-xs font-medium mb-6">
          <ShieldCheck className="h-3.5 w-3.5" />
          <span>Indian MSME Decarbonization Platform</span>
        </div>

        {/* Title */}
        <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight mb-6 bg-gradient-to-r from-emerald-600 via-teal-500 to-blue-600 bg-clip-text text-transparent">
          Decarbonize Your MSME,<br />
          <span className="text-neutral-900 dark:text-neutral-100">Monetize Your Sustainability</span>
        </h1>
        
        {/* Description */}
        <p className="max-w-2xl mx-auto text-lg md:text-xl text-neutral-500 dark:text-neutral-400 mb-10 leading-relaxed">
          The all-in-one Carbon Intelligence Platform to measure facility emissions, 
          verify eligibility, and transition from cost to credit revenue.
        </p>

        {/* Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-20">
          <Link href="/calculator">
            <Button size="lg" className="h-12 px-8 bg-emerald-600 hover:bg-emerald-700 text-white font-medium shadow-lg shadow-emerald-500/15 flex items-center gap-2 cursor-pointer">
              Calculate Footprint
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
          <Link href="/marketplace">
            <Button size="lg" variant="outline" className="h-12 px-8 border-neutral-300 dark:border-neutral-700 hover:bg-neutral-100 dark:hover:bg-neutral-800 font-medium cursor-pointer">
              Explore Marketplace
            </Button>
          </Link>
        </div>

        {/* Feature Grid */}
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4 text-left">
          {features.map((feature) => (
            <Link key={feature.href} href={feature.href} className="group">
              <Card className="h-full border border-neutral-200 dark:border-neutral-800 bg-white/70 dark:bg-neutral-900/50 backdrop-blur-md transition-all duration-300 group-hover:-translate-y-1.5 group-hover:border-emerald-500/30 group-hover:shadow-xl group-hover:shadow-emerald-500/5 cursor-pointer">
                <CardHeader className="p-6">
                  <div className={`w-12 h-12 rounded-lg ${feature.bg} flex items-center justify-center mb-4 transition-transform duration-300 group-hover:scale-110`}>
                    <feature.icon className={`h-6 w-6 ${feature.color}`} />
                  </div>
                  <CardTitle className="text-xl font-bold mb-2 group-hover:text-emerald-500 transition-colors">
                    {feature.title}
                  </CardTitle>
                  <CardDescription className="text-neutral-500 dark:text-neutral-400 leading-relaxed text-sm">
                    {feature.description}
                  </CardDescription>
                </CardHeader>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
