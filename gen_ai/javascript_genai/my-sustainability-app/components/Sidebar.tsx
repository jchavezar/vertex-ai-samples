import React from 'react';
import { FaCheckCircle } from 'react-icons/fa'; // You might need to install react-icons

const Sidebar = () => {
    return (
        <aside className="w-64 bg-white p-4 shadow-md flex flex-col text-gray-900">
            <h2 className="text-xl font-semibold mb-4">Sustainability Assistant</h2>
            <div className="mb-4">
                <h3 className="text-lg font-medium mb-2">Skills</h3>
                <div className="space-y-2">
                    <div className="bg-green-100 border border-green-500 text-green-800 p-2 rounded flex items-center justify-between">
                        <span>Sales accelerator</span>
                        <FaCheckCircle className="text-green-500" />
                    </div>
                    <div className="bg-gray-200 p-2 rounded">
                        Sustainability analysis
                    </div>
                </div>
            </div>
            {/* Placeholder for Prompt library */}
            <div className="mt-auto flex items-center text-blue-600">
                <span className="mr-2">💡</span> Prompt library
            </div>
        </aside>
    );
};

export default Sidebar;