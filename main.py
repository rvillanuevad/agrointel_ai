"""CLI entrypoint for AgroIntel AI."""

from __future__ import annotations

from utils.ai import DEFAULT_MODEL, generar_respuesta, generar_respuesta_regla
from utils.analysis import analizar_producto
from utils.data_loader import get_public_dataset_path, load_public_dataset


def cargar_datos():
    """Load and preprocess the public dataset used by the CLI."""
    return load_public_dataset()


def main() -> None:
    """Run the command-line workflow."""
    df = cargar_datos()
    productos = sorted(df["producto"].dropna().unique().tolist())

    print("=== AgroIntel AI ===")
    print(f"Dataset publico: {get_public_dataset_path()}")
    print("Productos disponibles:", ", ".join(productos))

    producto = input("Ingresa el producto a analizar: ").strip().lower()

    try:
        resultado = analizar_producto(df, producto)
        explicacion_rapida = generar_respuesta_regla(producto=producto, contexto=resultado)
        explicacion = generar_respuesta(producto=producto, contexto=resultado)

        print("\nResultado del analisis")
        print(f"Precios: {resultado['precios']}")
        print(f"Tendencia: {resultado['tendencia']}")
        print(f"Recomendacion: {resultado['recomendacion']}")
        print(f"Promedio movil corto: {resultado['promedio_movil']}")
        print(f"Region: {resultado['region']}")
        print(f"Mercado: {resultado['mercado']}")
        print(f"Precio actual: {resultado['precio_actual']:.2f}")
        print(f"Precio predicho: {resultado['precio_predicho']:.2f}")
        print(f"Clima: {resultado['clima_actual']}")
        print(f"Demanda: {resultado['demanda_actual']}")
        print("\nExplicacion inmediata")
        print(explicacion_rapida)
        print(f"\nExplicacion con IA ({DEFAULT_MODEL})")
        print(explicacion)
    except (ValueError, FileNotFoundError) as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()
