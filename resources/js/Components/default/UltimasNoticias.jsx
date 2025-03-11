import React, { useState, useEffect } from 'react';

function UltimasNoticias() {
    const [news, setNews] = useState([]);

    useEffect(() => {
        fetch('/api/latest-news') /* API de Noticias*/
            .then(response => response.json())
            .then(data => setNews(data));
    }, []);

    return (
        <div className="mt-4">
            <h2 className="text-center mb-3">Últimas Noticias</h2>
            <div className="list-group">
                {news.map((article, index) => (
                    <a key={index} href={article.url} className="list-group-item list-group-item-action">
                        {article.title}
                    </a>
                ))}
            </div>
        </div>
    );
}

export default UltimasNoticias;
