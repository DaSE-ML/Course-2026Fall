export class VmrPageError extends Error {
  constructor(message, code = 'VMR_PAGE_ERROR') {
    super(message);
    this.name = 'VmrPageError';
    this.code = code;
  }
}
