export default function SeccionBoletin() {
    return (
      <section className="py-16 bg-gray-900">
        <div className="container mx-auto px-4">
          <div className="bg-gradient-to-r from-red-800 to-red-600 rounded-xl p-8 md:p-12">
            <div className="max-w-3xl mx-auto text-center">
              <h2 className="text-3xl font-bold mb-4">MANTENTE AL DÍA</h2>
              <p className="text-lg mb-8">
                Suscríbete al boletín de F1 y recibe las últimas noticias, resultados de carreras y contenido exclusivo en
                tu bandeja de entrada.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
                <input
                  type="email"
                  placeholder="Tu dirección de correo"
                  className="px-4 py-3 rounded-md bg-white/10 border border-white/20 text-white placeholder:text-white/60 flex-grow focus:outline-none focus:ring-2 focus:ring-white/50"
                />
                <button className="bg-white text-red-600 hover:bg-gray-100 px-4 py-2 rounded-md">SUSCRIBIRSE</button>
              </div>
            </div>
          </div>
        </div>
      </section>
    )
  }
  
  