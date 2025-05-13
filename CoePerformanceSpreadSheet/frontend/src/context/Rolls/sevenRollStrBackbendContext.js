import React, { createContext, useState, useEffect } from 'react';

export const SevenRollStrBackbendContext = createContext();

export const SevenRollStrBackbendProvider = ({ children }) => {
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
        const saved = localStorage.getItem("sevenRollStrBackbendState");
        if (saved) {
            const parsed = JSON.parse(saved);
            if (parsed.subpageData) setSubpageData(parsed.subpageData);
            if (parsed.activePage) setActivePage(parsed.activePage);
        }
    }, []);

    // Save to localStorage on update
    useEffect(() => {
        localStorage.setItem("sevenRollStrBackbendState", JSON.stringify({ subpageData, activePage }));
    }, [subpageData, activePage]);

    return (
        <SevenRollStrBackbendContext.Provider value={{
            subpageData,
            setSubpageData,
            activePage,
            setActivePage
        }}>
            {children}
        </SevenRollStrBackbendContext.Provider>
    );
};
