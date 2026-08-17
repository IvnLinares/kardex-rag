"""Genera un CSV ficticio de ~50 registros de Kardex para el Día 2 (ingesta RAG)."""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

CATEGORIAS = {
    "Electrónica": [
        "Router WiFi 6",
        "Switch 24 puertos",
        "Cable UTP Cat6 (rollo)",
        "Disco SSD 1TB",
        "Memoria RAM 16GB DDR4",
        "Monitor 24 pulgadas",
        "Teclado mecánico",
        "Mouse inalámbrico",
        "Webcam Full HD",
        "Impresora láser",
    ],
    "Ferretería": [
        "Taladro percutor",
        "Set de destornilladores",
        "Cinta métrica 5m",
        "Martillo de goma",
        "Caja de tornillos autorroscantes",
        "Guantes de trabajo",
        "Casco de seguridad",
        "Cable eléctrico 2.5mm (rollo)",
        "Interruptor doble",
        "Tomacorriente doble",
    ],
    "Oficina": [
        "Resma de papel A4",
        "Caja de lapiceros azules",
        "Archivador tamaño oficio",
        "Grapadora industrial",
        "Caja de clips",
        "Marcador de pizarra",
        "Calculadora científica",
        "Silla ergonómica",
        "Escritorio metálico",
        "Pizarra acrílica 60x90",
    ],
    "Limpieza": [
        "Detergente industrial 5L",
        "Escoba de cerdas",
        "Trapeador microfibra",
        "Guantes de látex (caja)",
        "Desinfectante multiuso 1L",
        "Papel higiénico (paquete x12)",
        "Bolsas de basura (rollo x50)",
        "Alcohol en gel 1L",
        "Paño multiuso (paquete x5)",
        "Jabón líquido para manos 1L",
    ],
    "Repuestos": [
        "Correa de transmisión",
        "Filtro de aire industrial",
        "Rodamiento 6205",
        "Batería 12V 7Ah",
        "Fusible 10A (caja x10)",
        "Manguera hidráulica 1m",
        "Empaque de goma universal",
        "Bujía industrial",
        "Aceite lubricante 1L",
        "Correa en V tipo A",
    ],
}

BODEGAS = ["Bodega Central", "Bodega Norte", "Bodega Sur", "Bodega Este"]
ESTADOS = ["Disponible", "Bajo Stock", "Agotado", "En Tránsito"]

HOY = date(2026, 8, 17)


def build_rows() -> list[dict]:
    rows = []
    pid = 1000
    for categoria, productos in CATEGORIAS.items():
        for nombre in productos:
            pid += 1
            bodega = random.choice(BODEGAS)
            estado = random.choices(ESTADOS, weights=[55, 25, 10, 10])[0]
            if estado == "Agotado":
                cantidad = 0
            elif estado == "Bajo Stock":
                cantidad = random.randint(1, 15)
            else:
                cantidad = random.randint(20, 500)
            dias_atras = random.randint(0, 120)
            fecha = HOY - timedelta(days=dias_atras)
            rows.append(
                {
                    "producto_id": f"P-{pid}",
                    "nombre": nombre,
                    "categoria": categoria,
                    "bodega": bodega,
                    "cantidad": cantidad,
                    "fecha_ultimo_movimiento": fecha.isoformat(),
                    "estado": estado,
                }
            )
    return rows


def main() -> None:
    rows = build_rows()
    out_path = Path(__file__).resolve().parent.parent / "data" / "kardex.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "producto_id",
        "nombre",
        "categoria",
        "bodega",
        "cantidad",
        "fecha_ultimo_movimiento",
        "estado",
    ]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} filas escritas en {out_path}")


if __name__ == "__main__":
    main()
