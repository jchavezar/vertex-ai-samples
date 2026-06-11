import React from 'react';
import { Mail, Phone, MapPin, Instagram, Linkedin, Facebook } from './Icons';

export const Footer = () => {
  return (
    <footer id="contact" className="relative bg-black pt-24 pb-12 overflow-hidden border-t border-white/5">
      {/* Background Gradients */}
      <div className="absolute bottom-0 right-0 w-[400px] h-[400px] rounded-full bg-brand-lime/3 filter blur-[80px] pointer-events-none z-0" />

      {/* Footer Comet */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden z-0">
        <div className="absolute bottom-[20%] left-[-10%] w-[3px] h-[3px] rounded-full bg-white shadow-[0_0_8px_#fff] animate-footer-comet">
          <div className="absolute top-1/2 right-full w-[140px] h-[1.5px] bg-gradient-to-l from-white/95 via-white/40 to-transparent -translate-y-1/2 blur-[0.3px]" />
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 md:px-16 relative z-10">
        {/* Large Heading */}
        <div className="mb-20 text-center lg:text-left select-none">
          <h2 className="text-4xl md:text-7xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white via-white to-brand-lime/40 tracking-tight leading-[1.05]">
            LET'S BUILD <br className="hidden md:block" />
            SOMETHING.
          </h2>
        </div>

        {/* Footer Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 mb-16">
          {/* Col 1: Brand / Info */}
          <div>
            <h4 className="text-white font-black text-xl tracking-wider mb-6">UP DIGITAL.</h4>
            <p className="text-white/50 text-sm leading-relaxed mb-6">
              Miami's AI-powered digital marketing agency. We build websites, run ads, scale organic search, and engineer custom AI employees.
            </p>
            <div className="flex gap-4">
              <a href="https://instagram.com/helloupdigital" className="text-white/40 hover:text-brand-lime transition-colors">
                <Instagram className="w-5 h-5" />
              </a>
              <a href="https://linkedin.com" className="text-white/40 hover:text-brand-lime transition-colors">
                <Linkedin className="w-5 h-5" />
              </a>
              <a href="https://facebook.com" className="text-white/40 hover:text-brand-lime transition-colors">
                <Facebook className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Col 2: Services */}
          <div>
            <h4 className="text-white/40 text-xs font-black tracking-widest uppercase mb-6">Services</h4>
            <ul className="flex flex-col gap-3">
              <li><a href="#services" className="text-white/60 hover:text-white text-sm transition-colors">Web Design</a></li>
              <li><a href="#services" className="text-white/60 hover:text-white text-sm transition-colors">Social Media & UGC</a></li>
              <li><a href="#services" className="text-white/60 hover:text-white text-sm transition-colors">Meta & Google Ads</a></li>
              <li><a href="#services" className="text-white/60 hover:text-white text-sm transition-colors">AI SEO</a></li>
              <li><a href="#services" className="text-white/60 hover:text-white text-sm transition-colors">AI Assistants</a></li>
            </ul>
          </div>

          {/* Col 3: Company */}
          <div>
            <h4 className="text-white/40 text-xs font-black tracking-widest uppercase mb-6">Company</h4>
            <ul className="flex flex-col gap-3">
              <li><a href="#about" className="text-white/60 hover:text-white text-sm transition-colors">Solutions</a></li>
              <li><a href="#press" className="text-white/60 hover:text-white text-sm transition-colors">Press</a></li>
              <li><a href="#team" className="text-white/60 hover:text-white text-sm transition-colors">Team</a></li>
              <li><a href="#ai-employees" className="text-white/60 hover:text-white text-sm transition-colors">AI Employees</a></li>
            </ul>
          </div>

          {/* Col 4: Contact */}
          <div>
            <h4 className="text-white/40 text-xs font-black tracking-widest uppercase mb-6">Contact</h4>
            <ul className="flex flex-col gap-4">
              <li className="flex items-start gap-3">
                <MapPin className="w-5 h-5 text-brand-lime shrink-0 mt-0.5" />
                <span className="text-white/60 text-sm leading-relaxed">
                  1111 Brickell Ave Suite 3010, <br />
                  Miami, FL 33131
                </span>
              </li>
              <li className="flex items-center gap-3">
                <Mail className="w-5 h-5 text-brand-lime shrink-0" />
                <a href="mailto:helloupdigital@gmail.com" className="text-white/60 hover:text-white text-sm transition-colors">
                  helloupdigital@gmail.com
                </a>
              </li>
              <li className="flex items-center gap-3">
                <Phone className="w-5 h-5 text-brand-lime shrink-0" />
                <a href="tel:+17866085714" className="text-white/60 hover:text-white text-sm transition-colors">
                  +1 (786) 608-5714
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-white/5 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-white/30 text-xs">
            © {new Date().getFullYear()} Up Digital. All rights reserved.
          </p>
          <div className="flex gap-6">
            <a href="/privacy" className="text-white/30 hover:text-white/50 text-xs transition-colors">Privacy Policy</a>
            <a href="/terms" className="text-white/30 hover:text-white/50 text-xs transition-colors">Terms of Service</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
