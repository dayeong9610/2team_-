function Button({ children, onClick, disabled = false, }) {
    return (<button className="common-button" onClick={onClick} disabled={disabled}>
      {children}
    </button>);
}
export default Button;
