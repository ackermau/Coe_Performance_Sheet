import React from "react";
import { Routes, Route, Link } from "react-router-dom";
import RFQForm from "./components/RFQForm";
import MaterialSpecsForm from "./components/MaterialSpecsForm";
import EquipmentSummary from "./components/EquipmentSummary";
import TddbhdPage from "./components/TddbhdPage";

function App() {
    return (
        <div>
            <nav>
                <Link to="/">Home</Link> |
                <Link to="/rfq">Create RFQ</Link> |
                <Link to="/specs">Machine Specs</Link> |
                <Link to="/summary">Equipment Summary</Link> |
                <Link to="/tddbhd">TDDBHD</Link>
            </nav>

            <Routes>
                <Route path="/" element={<h1>Welcome to the Perfomance Web Sheet</h1>} />
                <Route path="/rfq" element={<RFQForm />} />
                <Route path="/specs" element={<MaterialSpecsForm rfqId={1} />} />
                <Route path="/summary" element={<EquipmentSummary rfqId={1} />} />
                <Route path="/tddbhd" element={<TddbhdPage />} /> 
            </Routes>
        </div>
    );
}

export default App;
