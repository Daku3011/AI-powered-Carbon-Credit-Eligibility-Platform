import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Calculator, FileText, MessageSquare, Store } from "lucide-react";

const features = [
  {
    title: "Carbon Calculator",
    description: "Calculate Scope 1 & 2 emissions and get AI-powered eligibility scoring for carbon credits.",
    href: "/calculator",
    icon: Calculator,
  },
  {
    title: "Project Marketplace",
    description: "Browse decarbonization projects with ROI, payback, and carbon credit potential.",
    href: "/marketplace",
    icon: Store,
  },
  {
    title: "Benchmarking Dashboard",
    description: "Compare your emissions against industry averages with interactive charts.",
    href: "/dashboard",
    icon: FileText,
  },
  {
    title: "AI Carbon Consultant",
    description: "Get answers about Indian carbon markets, policies, and registration processes.",
    href: "/chatbot",
    icon: MessageSquare,
  },
];

export default function Home() {
  return (
    <div className="container py-12">
      <div className="mx-auto max-w-2xl text-center mb-12">
        <h1 className="text-4xl font-bold tracking-tight mb-4">
          AI-powered Carbon Intelligence
        </h1>
        <p className="text-lg text-muted-foreground">
          Helping Indian MSMEs transition from carbon measurement to monetization.
          Get tailored insights for your industry.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {features.map((feature) => (
          <Link key={feature.href} href={feature.href}>
            <Card className="h-full hover:shadow-md transition-shadow cursor-pointer">
              <CardHeader>
                <feature.icon className="h-8 w-8 mb-2 text-primary" />
                <CardTitle className="text-lg">{feature.title}</CardTitle>
                <CardDescription>{feature.description}</CardDescription>
              </CardHeader>
            </Card>
          </Link>
        ))}
      </div>

      <div className="mt-12 text-center">
        <Link href="/calculator">
          <Button size="lg">Get Started</Button>
        </Link>
      </div>
    </div>
  );
}
