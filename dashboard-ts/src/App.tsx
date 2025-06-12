import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { unparse } from "papaparse";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";

type Factura = {
  id: number;
  nombre_archivo: string;
  proveedor: string;
  fecha: string;
  total: number;
};

function App() {

  const [facturas, setFacturas] = useState<Factura[]>([]);
  const [filtroProveedor, setFiltroProveedor] = useState("");
  const [fechaInicio, setFechaInicio] = useState("");
  const [fechaFin, setFechaFin] = useState("");
  const [facturaSeleccionada, setFacturaSeleccionada] = useState<Factura | null>(null);

  useEffect(() => {
    fetch("http://localhost:8000/facturas")
      .then((res) => res.json())
      .then((data) => setFacturas(data))
      .catch((err) => console.error("Error al cargar facturas:", err));
  }, []);

  const facturasFiltradas = facturas.filter((f) => {
    const coincideProveedor = f.proveedor
      .toLowerCase()
      .includes(filtroProveedor.toLowerCase());

    const fechaFactura = new Date(f.fecha);
    const desde = fechaInicio ? new Date(fechaInicio) : null;
    const hasta = fechaFin ? new Date(fechaFin) : null;

    const dentroDelRango =
      (!desde || fechaFactura >= desde) && (!hasta || fechaFactura <= hasta);

    return coincideProveedor && dentroDelRango;
  });

  function exportarFacturasCSV(facturas: Factura[]) {
    const csv = unparse(
      facturas.map((f) => ({
        ID: f.id,
        Proveedor: f.proveedor,
        Fecha: f.fecha,
        Archivo: f.nombre_archivo,
        Total: f.total?.toFixed(2),
      }))
    );

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "facturas_exportadas.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-3xl font-bold mb-4">📊 Dashboard de facturas</h1>

      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Filtrar por proveedor
        </label>
        <input
          type="text"
          placeholder="Ej. Makro, Frutas Javier..."
          className="w-full p-2 border border-gray-300 rounded-md shadow-sm"
          value={filtroProveedor}
          onChange={(e) => setFiltroProveedor(e.target.value)}
        />
      </div>

      <div className="mb-4 flex gap-4">
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Desde
          </label>
          <input
            type="date"
            className="w-full p-2 border border-gray-300 rounded-md shadow-sm"
            value={fechaInicio}
            onChange={(e) => setFechaInicio(e.target.value)}
          />
        </div>

        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Hasta
          </label>
          <input
            type="date"
            className="w-full p-2 border border-gray-300 rounded-md shadow-sm"
            value={fechaFin}
            onChange={(e) => setFechaFin(e.target.value)}
          />
        </div>
      </div>

      <Button
        variant="secondary"
        className="mb-4"
        onClick={() => exportarFacturasCSV(facturasFiltradas)}
      >
        Exportar a CSV
      </Button>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>ID</TableHead>
            <TableHead>Proveedor</TableHead>
            <TableHead>Fecha</TableHead>
            <TableHead>Archivo</TableHead>
            <TableHead className="text-right">Total (€)</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {facturasFiltradas.map((f) => (
            <TableRow
              key={f.id}
              onClick={() => setFacturaSeleccionada(f)}
              className="cursor-pointer hover:bg-gray-50"
            >
              <TableCell>{f.id}</TableCell>
              <TableCell>{f.proveedor}</TableCell>
              <TableCell>{f.fecha}</TableCell>
              <TableCell>{f.nombre_archivo}</TableCell>
              <TableCell className="text-right">{f.total?.toFixed(2)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <Dialog open={!!facturaSeleccionada} onOpenChange={() => setFacturaSeleccionada(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Factura #{facturaSeleccionada?.id}</DialogTitle>
            <DialogDescription>
              Detalles de la factura registrada.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-2">
            <p><strong>Proveedor:</strong> {facturaSeleccionada?.proveedor}</p>
            <p><strong>Fecha:</strong> {facturaSeleccionada?.fecha}</p>
            <p><strong>Archivo:</strong> {facturaSeleccionada?.nombre_archivo}</p>
            <p><strong>Total:</strong> {facturaSeleccionada?.total?.toFixed(2)} €</p>
          </div>
        </DialogContent>
      </Dialog>

    </div>
  );
}

export default App;



