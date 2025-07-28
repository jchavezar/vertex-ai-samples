import Image from 'next/image';
import React from 'react';

const Header = () => {
    return (
        <header className="bg-gray-800 text-white h-16 flex items-center justify-between px-4">
            <div className="flex items-center space-x-4">
                {/* Replace with your Deloitte logo */}
                <Image src="/deloitte-logo.png" alt="Deloitte Logo" width={100} height={30} />
                <nav className="space-x-4">
                    <a href="#" className="hover:underline">Home</a>
                    <a href="#" className="hover:underline">Insights Hub</a>
                    <a href="#" className="hover:underline">Research</a>
                    <a href="#" className="hover:underline">Sustainability Assistant</a>
                </nav>
            </div>
            <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center">
                MO
            </div>
        </header>
    );
};

export default Header;