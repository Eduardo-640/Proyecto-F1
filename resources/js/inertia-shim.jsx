import React, { useEffect, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';

export function Link({ href, children, method, ...rest }) {
  if (!method || method.toLowerCase() === 'get') {
    return <RouterLink to={href} {...rest}>{children}</RouterLink>;
  }

  const handle = (e) => {
    e.preventDefault();
    const form = document.createElement('form');
    form.method = method;
    form.action = href;
    document.body.appendChild(form);
    form.submit();
  };

  return (
    // eslint-disable-next-line jsx-a11y/anchor-is-valid
    <a href={href} onClick={handle} {...rest}>
      {children}
    </a>
  );
}

export function usePage() {
  // Provide a minimal compatibility layer. Consumers expect { props: { auth, ... } }
  return { props: window.APP || {} };
}

export function Head({ title, children }) {
  useEffect(() => {
    if (title) document.title = title;
    // If children contains a <title> element string, ignore for simplicity
  }, [title]);
  return null;
}

export function useForm(initial = {}) {
  const [data, setData] = useState(initial);
  const [errors, setErrors] = useState({});
  const [processing, setProcessing] = useState(false);

  function setField(key, value) {
    setData((p) => ({ ...p, [key]: value }));
  }

  function reset(...fields) {
    if (fields.length === 0) {
      setData(initial);
      return;
    }
    setData((p) => {
      const copy = { ...p };
      fields.forEach((f) => {
        copy[f] = initial[f];
      });
      return copy;
    });
  }

  async function submit(method, url) {
    setProcessing(true);
    try {
      const res = await fetch(url, {
        method: method.toUpperCase(),
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (res.redirected) window.location.href = res.url;
      const json = await res.json().catch(() => null);
      if (json && json.errors) setErrors(json.errors);
      setProcessing(false);
      return res;
    } catch (e) {
      setProcessing(false);
      throw e;
    }
  }

  return {
    data,
    setData,
    setField,
    errors,
    processing,
    post: (url) => submit('post', url),
    put: (url) => submit('put', url),
    delete: (url) => submit('delete', url),
    reset,
  };
}

export default {
  Link,
  usePage,
  Head,
  useForm,
};
