import React, { createContext, useState, useEffect } from 'react';

export const ElevenRollStrBackbendContext = createContext();

export const ElevenRollStrBackbendProvider = ({ children }) => {
    const defaultSubpageData = {
        page1: {}, // Max
        page2: {}, // Full
        page3: {}, // Min
        page4: {}, // Width
    };

    const [subpageData, setSubpageData] = useState(defaultSubpageData);
    const [activePage, setActivePage] = useState("page1");

    // Load from localStorage on mount
    useEffect(() => {
        const saved = localStorage.getItem("elevenRollStrBackbendState");
        if (saved) {
            const parsed = JSON.parse(saved);
            if (parsed.subpageData) setSubpageData(parsed.subpageData);
            if (parsed.activePage) setActivePage(parsed.activePage);
        }
    }, []);

    // Save to localStorage on update
    useEffect(() => {
        localStorage.setItem("elevenRollStrBackbendState", JSON.stringify({ subpageData, activePage }));
    }, [subpageData, activePage]);

    return (
        <ElevenRollStrBackbendContext.Provider value={{
            subpageData,
            setSubpageData,
            activePage,
            setActivePage
        }}>
            {children}
        </ElevenRollStrBackbendContext.Provider>
    );
};