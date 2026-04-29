<%
Dim conn, rs
Set conn = Server.CreateObject("ADODB.Connection")
conn.Open "Driver={MySQL};Server=localhost;Database=tigerex;Uid=root;Pwd=pass;"
' Same backend for all ASP apps
%>
