import streamlit as st

# Using st.latex()
st.latex(r'\int a x^2 \,dx')

# Using st.write() with LaTeX formatting
st.write("Here's another equation: $$x^2 + y^2 = z^2$$")

# Combining st.write() and f-strings
latex_expression = r"\frac{1}{2} \cdot a \cdot b"
st.write(f"The area of a triangle is:  ${latex_expression}$")