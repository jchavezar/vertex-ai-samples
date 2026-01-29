import { useDashboardStore } from '../../store/dashboardStore';
import { X } from 'lucide-react';

export const AdkOverlay = () => {
    const { isAdkOverlayOpen, setAdkOverlayOpen } = useDashboardStore();

    if (!isAdkOverlayOpen) return null;

    return (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-8 backdrop-blur-xl bg-black/80">
            {/* Outer grid pattern for context */}
            <div className="absolute inset-0 bg-grid-white/[0.05] bg-[size:40px_40px] pointer-events-none opacity-20" />
            
            <button 
                onClick={() => setAdkOverlayOpen(false)}
                className="absolute top-8 right-8 p-3 rounded-full bg-white/10 hover:bg-white/20 text-white transition-all z-50 group border border-white/20 hover:scale-110 active:scale-95 shadow-lg shadow-white/5"
            >
                <X size={32} className="group-hover:rotate-90 transition-transform" />
            </button>

            {/* Dashboard-Style Modal Container - Transparent for Floating Image */}
            <div className="relative w-full max-w-[90vw] h-[85vh] rounded-[3rem] overflow-hidden p-8 flex flex-col items-center justify-center pointer-events-none">

                {/* Image Container */}
                <div className="relative w-full h-full p-12 flex items-center justify-center pointer-events-auto">
                    <img
                        src="/architecture_diagram.jpeg"
                        alt="System Architecture"
                        className="max-w-full max-h-full object-contain filter drop-shadow-2xl"
                        onError={(e) => {
                            e.currentTarget.src = "https://placehold.co/1200x800/1a1a1a/white?text=Architecture+Diagram+Missing";
                        }}
                    />
                </div>
            </div>
        </div>
    );
};
