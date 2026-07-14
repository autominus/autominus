import { r as a, s as c, G as s } from "./index-DXKy-3Kg.js";
const m=s("auth",()=>{const e=a(localStorage.getItem("ft_token")||""),t=a(JSON.parse(localStorage.getItem("ft_user")||"null")),l=c(()=>!!e.value);function r(n){const o={id:1,username:n||"小明同学"};e.value="mock-"+Date.now(),t.value=o,localStorage.setItem("ft_token",e.value),localStorage.setItem("ft_user",JSON.stringify(o))}function u(){e.value="",t.value=null,localStorage.removeItem("ft_token"),localStorage.removeItem("ft_user")}return{token:e,user:t,isLoggedIn:l,login:r,logout:u}});export { m as u };

