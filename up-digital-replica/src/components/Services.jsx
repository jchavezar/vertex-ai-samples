import React from 'react';
import { Layout, Share2, Target, Search, Cpu, Heart } from './Icons';

const SERVICES = [
  {
    id: '01',
    title: 'Web Design',
    desc: 'Custom websites built for performance, UX, and conversions — zero templates.',
    details: 'React, Next.js, interactive animations, and head-turning user interfaces grounded in business metrics.',
    Icon: Layout,
  },
  {
    id: '02',
    title: 'Social Media',
    desc: 'Viral reels, UGC, influencer collabs, and full-funnel Instagram & TikTok strategy.',
    details: 'Content calendars, scripting, video editing, and community growth hacking to get you in front of millions.',
    Icon: Share2,
  },
  {
    id: '03',
    title: 'Meta & Google Ads',
    desc: 'High-ROI paid campaigns with advanced targeting and creative optimization.',
    details: 'A/B testing of ads copy, design, landing pages, and smart bidding models that maximize conversion values.',
    Icon: Target,
  },
  {
    id: '04',
    title: 'AI SEO',
    desc: 'AI-driven content generation, technical audits, and rank tracking that scales.',
    details: 'Outranking competitors by pairing keyword cluster analysis with semantic matching tools for topical authority.',
    Icon: Search,
  },
  {
    id: '05',
    title: 'AI Employees & Automations',
    desc: 'Custom AI chatbots and workflows that automate customer service and marketing.',
    details: 'Retrieval Augmented Generation (RAG) agents that work 24/7, ingest your docs, and qualify leads autonomously.',
    Icon: Cpu,
  },
  {
    id: '06',
    title: 'Non-Profit Management',
    desc: 'Google Ad Grants management, donor acquisition, and storytelling campaigns.',
    details: 'Securing and maximizing the $10,000/month Google Grant to drive advocacy, donations, and community impact.',
    Icon: Heart,
  }
];

export const Services = () => {
  return (
    <section id="services" className="relative pt-24 pb-20 bg-black border-t border-white/5">
      <div className="max-w-7xl mx-auto px-6 md:px-16">
        {/* Section Header */}
        <div className="mb-16">
          <span className="text-[10px] font-black tracking-[0.3em] uppercase text-brand-lime block mb-3 animate-[pcap-blink_1.5s_infinite]">
            SERVICES
          </span>
          <h2 className="text-3xl md:text-5xl font-black text-white tracking-tight mb-4">
            W H A T   W E   D O .
          </h2>
          <p className="text-white/40 text-sm uppercase tracking-wider">
            Hover any card to see details.
          </p>
        </div>

        {/* Grid of Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {SERVICES.map((service) => {
            const { Icon } = service;
            return (
              <div 
                key={service.id} 
                className="group h-[320px] [perspective:1000px] cursor-pointer"
              >
                {/* Flipping Card Container */}
                <div className="relative w-full h-full transition-transform duration-700 [transform-style:preserve-3d] group-hover:[transform:rotateY(180deg)]">
                  
                  {/* Front Side */}
                  <div className="absolute inset-0 w-full h-full bg-brand-dark border border-white/5 rounded-2xl p-8 flex flex-col justify-between [backface-visibility:hidden] z-2 shadow-lg">
                    <div className="flex justify-between items-start">
                      <div className="p-3 bg-white/5 rounded-xl border border-white/5 text-brand-lime">
                        <Icon className="w-6 h-6" />
                      </div>
                      <span className="text-white/20 text-xs font-black tracking-widest">{service.id}</span>
                    </div>
                    <div>
                      <h3 className="text-white font-bold text-xl mb-3">{service.title}</h3>
                      <p className="text-white/60 text-sm leading-relaxed">{service.desc}</p>
                    </div>
                  </div>

                  {/* Back Side */}
                  <div className="absolute inset-0 w-full h-full bg-brand-lime rounded-2xl p-8 flex flex-col justify-between [backface-visibility:hidden] [transform:rotateY(180deg)] z-1 shadow-lg shadow-brand-lime/5">
                    <div className="flex justify-between items-start">
                      <div className="p-3 bg-brand-dark-alt rounded-xl text-brand-lime">
                        <Icon className="w-6 h-6" />
                      </div>
                      <span className="text-brand-dark-alt/50 text-xs font-black tracking-widest">{service.id}</span>
                    </div>
                    <div>
                      <h3 className="text-brand-dark-alt font-black text-xl mb-3">{service.title}</h3>
                      <p className="text-brand-dark-alt/80 text-sm leading-relaxed font-semibold">{service.details}</p>
                    </div>
                  </div>

                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default Services;
