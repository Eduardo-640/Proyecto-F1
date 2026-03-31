import React, { useState } from 'react'

const DefaultItems = [
	{ key: 'home', label: 'Inicio', href: '/' },
	{ key: 'races', label: 'Carreras', href: '/races' },
	{ key: 'teams', label: 'Equipos', href: '/teams' },
	{ key: 'drivers', label: 'Pilotos', href: '/drivers' },
]

export default function Sidebar({ items = DefaultItems, logo, className = '', selected, onSelect }) {
	const [open, setOpen] = useState(false)

	function handleSelect(e, it) {
		e.preventDefault()
		if (typeof onSelect === 'function') onSelect(it.key)
		setOpen(false)
	}

	return (
		<>
			{/* Mobile: hamburger */}
			<button
				aria-label={open ? 'Cerrar menú' : 'Abrir menú'}
				className="md:hidden fixed top-4 left-4 z-40 p-2 rounded-md bg-gray-900/95 shadow-lg text-gray-100"
				onClick={() => setOpen((v) => !v)}
			>
				<svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					{open ? (
						<path strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
					) : (
						<path strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
					)}
				</svg>
			</button>

			{/* Backdrop for mobile when open */}
			<div
				onClick={() => setOpen(false)}
				className={`fixed inset-0 bg-black/50 z-30 transition-opacity md:hidden ${open ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`}
			/>

			{/* Sidebar */}
			<aside
				className={`fixed top-0 left-0 h-full z-40 transform bg-gray-900 text-gray-100 border-r border-gray-800 shadow-sm transition-transform duration-200 w-64 ${
					open ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
				} md:static md:translate-x-0 md:min-h-screen min-h-screen ${className}`}
				style={{}}
				role="navigation"
			>
				<div className="h-full flex flex-col">


					<nav className="flex-1 px-2 py-4 space-y-1">
						{items.map((it) => {
							const active = selected === it.key
							return (
								<a
									key={it.key}
									href={it.href}
									onClick={(e) => {
										// Only prevent navigation if parent passed an onSelect handler
										if (typeof onSelect === 'function') {
											handleSelect(e, it)
											return
										}
										// If no onSelect provided, allow the link to behave as normal
									}}
									aria-current={active ? 'page' : undefined}
									className={`group flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
										active ? 'bg-gray-800 text-white' : 'text-gray-200 hover:bg-gray-800 hover:text-white'
									}`}
								>
									<span className={`w-6 h-6 rounded flex items-center justify-center text-sm ${active ? 'bg-red-500 text-white' : 'bg-gray-700 text-gray-200'}`}>•</span>
									<span className="truncate">{it.label}</span>
								</a>
							)
						})}
					</nav>

					<div className="absolute bottom-0 left-0 w-full px-4 py-3 border-t border-gray-800 bg-gray-900">
						<div className="flex gap-3">
							<a
								href="/steam"
								onClick={(e) => {
									if (typeof onSelect === 'function') {
										e.preventDefault()
										onSelect('steam')
									}
								}}
								className="flex-1 text-sm text-gray-200 hover:text-white"
							>
								Steam
							</a>
							<a
								href="/subscribe"
								onClick={(e) => {
									if (typeof onSelect === 'function') {
										e.preventDefault()
										onSelect('subscribe')
									}
								}}
								className="flex-1 text-sm text-gray-200 hover:text-white text-right"
							>
								Suscripción
							</a>
						</div>
					</div>
				</div>
			</aside>
		</>
	)
}

