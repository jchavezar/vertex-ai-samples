import React from 'react';

export const About = () => {
  return (
    <section id="about" className="relative overflow-hidden pt-24 pb-20 bg-brand-light">
      <div className="max-w-7xl mx-auto px-6 md:px-16 flex flex-col md:flex-row gap-12 items-start justify-between">
        <div className="max-w-md">
          <span className="text-[10px] font-black tracking-[0.3em] uppercase text-brand-dark-alt/50 block mb-3">
            More Than An Agency
          </span>
          <h2 className="text-3xl md:text-5xl font-black text-brand-dark-alt leading-[1.15] tracking-tight">
            WE ARE YOUR IN-HOUSE MARKETING TEAM.
          </h2>
        </div>
        <div className="max-w-xl flex flex-col gap-6">
          <p className="text-brand-dark-alt/70 text-lg leading-relaxed">
            We're a forward-thinking marketing agency blending creativity with the power of AI. From SEO and paid advertising to viral social media and custom AI assistants, we develop systems that grow brands.
          </p>
          <p className="text-brand-dark-alt/70 text-lg leading-relaxed">
            Our team is composed of certified experts who understand how to leverage AI to deliver results faster and more efficiently than traditional agencies.
          </p>
          <div className="flex gap-4 mt-4">
            <a href="#services" className="px-6 py-3 rounded-xl bg-brand-dark-alt text-white font-bold text-sm hover:bg-brand-dark transition-colors">
              Our Services
            </a>
            <a href="#team" className="px-6 py-3 rounded-xl border border-brand-dark-alt/10 text-brand-dark-alt font-bold text-sm hover:bg-brand-dark-alt/5 transition-colors">
              Meet the Team
            </a>
          </div>
        </div>
      </div>
    </section>
  );
};

export default About;
