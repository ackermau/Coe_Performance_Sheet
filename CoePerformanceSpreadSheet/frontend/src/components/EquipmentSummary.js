import { useEffect, useState, useContext } from "react";
import { RFQFormContext } from "../context/RFQFormContext";
import { MaterialSpecsContext } from "../context/MaterialSpecsContext";

export default function EquipmentSummary({ rfqId }) {
    const { rfqForm } = useContext(RFQFormContext);
    const { materialSpecs } = useContext(MaterialSpecsContext);
    const [rfq, setRFQ] = useState(null);

    useEffect(() => {
        const fetchRFQ = async () => {
            const response = await fetch(`/api/rfq/${rfqId}`);
            const data = await response.json();
            setRFQ(data);
        };
        fetchRFQ();
    }, [rfqId]);

    return (
        <div>
            <h1 className="text-xl font-bold">Equipment Summary</h1>
            {rfq ? (
                <div>
                    <p>Customer: {rfq.customer_name}</p>
                    <p>Project: {rfq.project_name}</p>
                    <h2 className="text-lg font-semibold mt-4">Machines</h2>
                    <ul>
                        {rfq.machines && rfq.machines.map((machine, index) => (
                            <li key={index}>{machine.name} ({machine.type})</li>
                        ))}
                    </ul>
                </div>
            ) : (
                <p>Loading...</p>
            )}
        </div>
    );
}