import { Calendar, ChevronRight, Clock } from "lucide-react"


export default function SeccionProximasCarreras() {
    return (
        <div className="container mx-auto px-4 z-30">
            <div className="flex flex-col md:flex-row items-center justify-between bg-gray-800 rounded-xl p-6 md:p-8">
                <div>
                    <div className="text-red-500 font-medium mb-2">PROXIMA CARRERA</div>
                    <h2 className="text-2xl md:text-3xl font-bold mb-2">MONACO GRAND PRIX</h2>
                    <div className="flex items-center gap-4 text-gray-300">
                        <div className="flex items-center">
                            <Calendar className="h-4 w-4 mr-2" />
                            <span>26-28 MAY</span>
                        </div>
                        <div className="flex items-center">
                            <Clock className="h-4 w-4 mr-2" />
                            <span>15:00 UTC</span>
                        </div>
                    </div>
                </div>
                <div className="mt-6 md:mt-0">
                    <button className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md flex items-center">
                        MAS DETALLES <ChevronRight className="h-4 w-4 ml-2" />
                    </button>
                </div>
            </div>
        </div>
    );
}