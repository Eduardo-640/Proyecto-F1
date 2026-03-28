import React from 'react';
import { Navigate } from 'react-router-dom';

export default function Welcome() {
    return <Navigate to="/" replace />;
}
