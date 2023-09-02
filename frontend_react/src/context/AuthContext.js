import { createContext, useState, useEffect } from "react";
import jwt_decode from "jwt-decode";
import { useHistory } from "react-router-dom";

const AuthContext = createContext();

export default AuthContext;

export const AuthProvider = ({ children }) => {
  const [authTokens, setAuthTokens] = useState(() =>
    localStorage.getItem("authTokens")
      ? JSON.parse(localStorage.getItem("authTokens"))
      : null
  );
  const [user, setUser] = useState(() =>
    localStorage.getItem("authTokens")
      ? jwt_decode(localStorage.getItem("authTokens"))
      : null
  );
  let [loading, setLoading] = useState(true);
  const BASE_URL = `http://${window.location.hostname}:3000/api`;

  const history = useHistory();
  //login
  let loginUser = async (e) => {
    e.preventDefault();
    let response = await fetch(`${BASE_URL}/token/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: e.target.email.value,
        password: e.target.password.value,
      }),
    });
    let data = await response.json();

    if (response.status === 200) {
      setAuthTokens(data);
      setUser(jwt_decode(data.access));
      localStorage.setItem("authTokens", JSON.stringify(data));
      history.push("/");
      window.location.reload();
    } else if (response.status === 500) {
      console.log("Неполадки на сервере");
      document.body.innerHTML = '<h1>Неполадки на сервере</h1>';
    } else if (response.status === 401) {
      console.log("введен неккоректный email или пароль");
      document.body.innerHTML = '<h1>Введен некорректный email или пароль</h1>';
    } else {
      console.log(response.status);
      document.body.innerHTML = '<h1>Неизвестная ошибка</h1>';
    }
  };
  //registration
  const register = async (e) => {
    e.preventDefault();
    let response = await fetch(`${BASE_URL}/users/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: e.target.email.value,
        password: e.target.password.value,
        first_name: e.target.first_name.value,
        last_name: e.target.last_name.value,
        phone: e.target.phone.value,
      }),
    });

    if (response.status === 201) {
      history.push("/sign-in");
    } else if (response.status === 500) {
      console.log("Неполадки на сервере");
    } else if (response.status === 400) {
      const data = await response.json();
      console.log("Ошибка", data);
      document.body.innerHTML = '<h1>Введены некорректные данные</h1>';
      document.body.innerHTML += `<p>${JSON.stringify(data)}</p>`;
    }
  };
  //send link to the email
  const sendLink = async (email) => {
    return await fetch(`${BASE_URL}/users/reset_password/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(email),
    });
  };
// change password
const changePassword = async (data) => {
  let response = await fetch(`${BASE_URL}/users/reset_password_confirm/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (response.status === 201) {
    console.log("Пароль успешно изменен");
  } else if (response.status === 500) {
    console.log("Неполадки на сервере");
  } else if (response.status === 400) {
    const errorData = await response.json();
    console.log("Ошибка", errorData);
    document.body.innerHTML = '<h1>Введены некорректные данные</h1>';
    document.body.innerHTML += `<p>${JSON.stringify(errorData)}</p>`;
  }
};

  let contextData = {
    user: user,
    authTokens: authTokens,
    setAuthTokens: setAuthTokens,
    setUser: setUser,
    loginUser: loginUser,
    register: register,
    sendLink: sendLink,
    changePassword: changePassword,
  };

  useEffect(() => {
    if (authTokens) {
      setUser(jwt_decode(authTokens.access));
    }
    setLoading(false);
  }, [authTokens, loading]);

  return (
    <AuthContext.Provider value={contextData}>
      {loading ? null : children}
    </AuthContext.Provider>
  );
};
