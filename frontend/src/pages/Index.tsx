import Hero from "@/components/dashboard/Hero";
import BurndownCard from "@/components/dashboard/BurndownCard";
import StandupCard from "@/components/dashboard/StandupCard";
import BacklogCard from "@/components/dashboard/BacklogCard";
import SprintPlanningCard from "@/components/dashboard/SprintPlanningCard";
import { SEO } from "@/components/SEO";

const Index = () => {
  const title = "AI Scrum Master Dashboard";
  const description = "Automate standups, backlog grooming, sprint planning and burndown insights with human-in-the-loop oversight.";
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: title,
    description,
    applicationCategory: "ProjectManagementApplication",
    operatingSystem: "Web",
    offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
  };

  return (
    <main className="container mx-auto min-h-screen space-y-8 py-10">
      <SEO title={title} description={description} canonical={"/"} jsonLd={jsonLd} />
      <Hero />
      <section className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div className="md:col-span-2 lg:col-span-2">
          <BurndownCard />
        </div>
        <StandupCard />
        <BacklogCard />
        <SprintPlanningCard />
      </section>
    </main>
  );
};

export default Index;
